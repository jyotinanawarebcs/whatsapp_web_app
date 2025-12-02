from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Sum
from .models import Automation, AutomationLog
from .serializers import (
    AutomationSerializer, AutomationCreateSerializer,
    AutomationLogSerializer
)
from .tasks import execute_automation_task

class AutomationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing automations.
    """
    def get_queryset(self):
        """
        TEMPORARY: Return all automations (remove user filter)
        """
        return Automation.objects.all()  # ✅ REMOVE: .filter(user=self.request.user)
    
    def get_serializer_class(self):
        """
        Use different serializer for creation vs retrieval.
        """
        if self.action == 'create':
            return AutomationCreateSerializer
        return AutomationSerializer
    
    def perform_create(self, serializer):
        """
        Handle automation creation.
        """
        automation = serializer.save()
        
        # If automation is active, schedule it
        if automation.status == 'active':
            from .tasks import schedule_single_automation
            schedule_single_automation.delay(automation.id)
    
    @action(detail=True, methods=['post'])
    def toggle_status(self, request, pk=None):
        """
        Toggle automation status between active and paused.
        """
        automation = self.get_object()
        
        if automation.status == 'active':
            automation.status = 'paused'
        else:
            automation.status = 'active'
            # Schedule in Celery if becoming active
            from .tasks import schedule_single_automation
            schedule_single_automation.delay(automation.id)
        
        automation.save()
        
        return Response({
            'status': automation.status,
            'message': f'Automation {automation.name} is now {automation.status}'
        })
    
    @action(detail=True, methods=['post'])
    def run_now(self, request, pk=None):
        """
        Execute automation immediately.
        """
        automation = self.get_object()
        execute_automation_task.delay(automation.id)
        
        return Response({
            'message': f'Automation {automation.name} started immediately'
        })
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get automation statistics for dashboard.
        """
        automations = self.get_queryset()
        
        # Count active automations
        active_count = automations.filter(status='active').count()
        
        # Count automations scheduled for today
        today = timezone.now().date()
        scheduled_today = automations.filter(
            status='active',
            next_run__date=today
        ).count()
        
        # Calculate total messages sent
        total_sent = automations.aggregate(
            total=Sum('messages_sent')
        )['total'] or 0
        
        return Response({
            'active_automations': active_count,
            'scheduled_today': scheduled_today,
            'total_sent': total_sent
        })

class AutomationLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing automation execution logs.
    """
    serializer_class = AutomationLogSerializer
    
    def get_queryset(self):
        """
        TEMPORARY: Return all logs (remove user filter)
        """
        return AutomationLog.objects.all().order_by('-run_time')  # ✅ REMOVE user filter