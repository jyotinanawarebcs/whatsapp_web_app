import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { 
  Plus, 
  Calendar, 
  Cake, 
  PartyPopper, 
  Clock, 
  Play, 
  Pause, 
  Edit, 
  Trash2, 
  Loader2,
  Megaphone,
  RefreshCw,
  CheckCircle,
  XCircle,
  AlertCircle
} from "lucide-react";
import { automationsAPI, formatAutomationType, formatStatus, getStatusColor, formatDate, Automation } from "@/services/api";
import { useToast } from "@/components/ui/use-toast";
import CreateCampaignModal from "@/components/CreateCampaignModal"; // ✅ Import campaign modal

const Automations = () => {
  const [automations, setAutomations] = useState<Automation[]>([]);
  const [stats, setStats] = useState({
    active_automations: 0,
    scheduled_today: 0,
    total_sent: 0
  });
  const [loading, setLoading] = useState(true);
  const [loadingStates, setLoadingStates] = useState<Record<number, boolean>>({});
  const [isCreateCampaignOpen, setIsCreateCampaignOpen] = useState(false); // ✅ Campaign modal state
  const { toast } = useToast();

  // Type icons mapping
  const typeIcons: Record<string, React.ReactNode> = {
    birthday: <Cake className="h-5 w-5" />,
    festival: <PartyPopper className="h-5 w-5" />,
    reminder: <Clock className="h-5 w-5" />,
    followup: <Calendar className="h-5 w-5" />,
    custom: <Megaphone className="h-5 w-5" />,
  };

  // Status icons
  const statusIcons: Record<string, React.ReactNode> = {
    active: <CheckCircle className="h-4 w-4 text-success" />,
    paused: <Pause className="h-4 w-4 text-warning" />,
    draft: <AlertCircle className="h-4 w-4 text-muted-foreground" />,
  };

  // Fetch automations and stats
  const fetchData = async () => {
    try {
      setLoading(true);
      const [automationsData, statsData] = await Promise.all([
        automationsAPI.getAll(),
        automationsAPI.getStats()
      ]);
      setAutomations(automationsData);
      setStats(statsData);
    } catch (error: any) {
      console.error('Error fetching data:', error);
      toast({
        title: "Error",
        description: "Failed to fetch automations",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  // Handle toggle status
  const handleToggleStatus = async (id: number) => {
    try {
      setLoadingStates(prev => ({ ...prev, [id]: true }));
      const result = await automationsAPI.toggleStatus(id);
      
      // Update local state
      setAutomations(prev => prev.map(auto => 
        auto.id === id 
          ? { ...auto, status: result.status as 'active' | 'paused' | 'draft' }
          : auto
      ));
      
      // Refresh stats
      const newStats = await automationsAPI.getStats();
      setStats(newStats);
      
      toast({
        title: "Success",
        description: result.message,
      });
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message || "Failed to toggle automation status",
        variant: "destructive",
      });
    } finally {
      setLoadingStates(prev => ({ ...prev, [id]: false }));
    }
  };

  // Handle run now
  const handleRunNow = async (id: number) => {
    try {
      setLoadingStates(prev => ({ ...prev, [id]: true }));
      const result = await automationsAPI.runNow(id);
      
      toast({
        title: "Success",
        description: result.message,
      });
      
      // Refresh data after running
      setTimeout(fetchData, 2000);
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message || "Failed to run automation",
        variant: "destructive",
      });
    } finally {
      setLoadingStates(prev => ({ ...prev, [id]: false }));
    }
  };

  // Handle delete
  const handleDelete = async (id: number, name: string) => {
    if (!confirm(`Are you sure you want to delete "${name}"?`)) {
      return;
    }
    
    try {
      setLoadingStates(prev => ({ ...prev, [id]: true }));
      await automationsAPI.delete(id);
      
      // Remove from local state
      setAutomations(prev => prev.filter(auto => auto.id !== id));
      
      // Refresh stats
      const newStats = await automationsAPI.getStats();
      setStats(newStats);
      
      toast({
        title: "Success",
        description: "Automation deleted successfully",
      });
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message || "Failed to delete automation",
        variant: "destructive",
      });
    } finally {
      setLoadingStates(prev => ({ ...prev, [id]: false }));
    }
  };

  // Handle campaign created
  const handleCampaignCreated = (campaign: any) => {
    toast({
      title: "Campaign Created",
      description: `${campaign.name || campaign.campaign_name} has been created successfully!`,
    });
    // Yahan aap campaign created hone par kuch aur action kar sakte ho
    console.log("Campaign created:", campaign);
  };

  // Initial data fetch
  useEffect(() => {
    fetchData();
  }, []);

  // Loading state
  if (loading) {
    return (
      <div className="p-4 sm:p-6 flex items-center justify-center h-screen">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary mx-auto mb-4" />
          <p className="text-muted-foreground">Loading automations...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 sm:p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Automations</h1>
          <p className="mt-1 text-muted-foreground">Scheduled campaigns and automated messages</p>
        </div>
        
        <div className="flex gap-2">
          <Button 
            variant="outline"
            size="sm"
            onClick={fetchData}
            disabled={loading}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          
          <Button 
            className="w-full sm:w-auto bg-primary hover:bg-primary/90"
            onClick={() => setIsCreateCampaignOpen(true)}
          >
            <Plus className="h-5 w-5 mr-2" />
            New Campaign
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <div className="rounded-lg bg-success/10 p-3">
                <Play className="h-6 w-6 text-success" />
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground">Active Automations</p>
                <h3 className="text-2xl font-bold text-foreground">
                  {stats.active_automations}
                </h3>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <div className="rounded-lg bg-primary/10 p-3">
                <Calendar className="h-6 w-6 text-primary" />
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground">Scheduled Today</p>
                <h3 className="text-2xl font-bold text-foreground">
                  {stats.scheduled_today}
                </h3>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <div className="rounded-lg bg-warning/10 p-3">
                <Clock className="h-6 w-6 text-warning" />
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground">Total Messages Sent</p>
                <h3 className="text-2xl font-bold text-foreground">
                  {stats.total_sent.toLocaleString()}
                </h3>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Automation List */}
      <div className="space-y-4">
        {automations.length === 0 ? (
          <Card>
            <CardContent className="p-12 text-center">
              <Cake className="h-12 w-12 mx-auto text-muted-foreground/50 mb-4" />
              <h3 className="text-lg font-medium text-foreground mb-2">No automations yet</h3>
              <p className="text-muted-foreground mb-6">Create your first campaign to get started</p>
              <Button onClick={() => setIsCreateCampaignOpen(true)}>
                <Plus className="h-4 w-4 mr-2" />
                Create First Campaign
              </Button>
            </CardContent>
          </Card>
        ) : (
          automations.map((automation) => {
            const statusColor = getStatusColor(automation.status);
            
            return (
              <Card key={automation.id} className="hover:shadow-lg transition-shadow">
                <CardContent className="p-6">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex gap-4 flex-1">
                      <div className={`flex h-12 w-12 items-center justify-center rounded-lg ${statusColor.bg} ${statusColor.text}`}>
                        {typeIcons[automation.automation_type] || <Megaphone className="h-5 w-5" />}
                      </div>
                      
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="font-semibold text-foreground truncate">
                            {automation.name}
                          </h3>
                          <Badge
                            variant="outline"
                            className={`${statusColor.bg} ${statusColor.text} ${statusColor.border}`}
                          >
                            <span className="flex items-center gap-1">
                              {statusIcons[automation.status]}
                              {formatStatus(automation.status)}
                            </span>
                          </Badge>
                        </div>
                        
                        <div className="flex flex-wrap items-center gap-4 mb-3 text-sm text-muted-foreground">
                          <span className="flex items-center gap-1">
                            {typeIcons[automation.automation_type]}
                            {formatAutomationType(automation.automation_type)}
                          </span>
                          <span>•</span>
                          <span>{automation.schedule_type}</span>
                        </div>
                        
                        <div className="grid grid-cols-3 gap-4 text-sm">
                          <div>
                            <p className="text-muted-foreground">Last Run</p>
                            <p className="font-medium text-foreground">
                              {formatDate(automation.last_run)}
                            </p>
                          </div>
                          <div>
                            <p className="text-muted-foreground">Next Run</p>
                            <p className="font-medium text-foreground">
                              {formatDate(automation.next_run) || "Not scheduled"}
                            </p>
                          </div>
                          <div>
                            <p className="text-muted-foreground">Messages Sent</p>
                            <p className="font-medium text-foreground">
                              {automation.messages_sent?.toLocaleString() || 0}
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex flex-col sm:flex-row gap-2">
                      <Button 
                        size="sm" 
                        variant="outline"
                        onClick={() => handleToggleStatus(automation.id)}
                        disabled={loadingStates[automation.id]}
                        className="h-9 w-9 p-0 sm:w-auto sm:px-3"
                      >
                        {loadingStates[automation.id] ? (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        ) : automation.status === "active" ? (
                          <Pause className="h-4 w-4" />
                        ) : (
                          <Play className="h-4 w-4" />
                        )}
                        <span className="hidden sm:inline ml-2">
                          {automation.status === "active" ? "Pause" : "Activate"}
                        </span>
                      </Button>
                      
                      <Button 
                        size="sm" 
                        variant="outline"
                        onClick={() => handleRunNow(automation.id)}
                        disabled={loadingStates[automation.id]}
                        className="h-9 w-9 p-0 sm:w-auto sm:px-3"
                      >
                        {loadingStates[automation.id] ? (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                          <Play className="h-4 w-4" />
                        )}
                        <span className="hidden sm:inline ml-2">Run Now</span>
                      </Button>
                      
                      <Button 
                        size="sm" 
                        variant="outline"
                        onClick={() => {
                          toast({
                            title: "Coming Soon",
                            description: "Edit feature will be available soon",
                          });
                        }}
                        className="h-9 w-9 p-0 sm:w-auto sm:px-3"
                      >
                        <Edit className="h-4 w-4" />
                        <span className="hidden sm:inline ml-2">Edit</span>
                      </Button>
                      
                      <Button 
                        size="sm" 
                        variant="outline"
                        onClick={() => handleDelete(automation.id, automation.name)}
                        disabled={loadingStates[automation.id]}
                        className="h-9 w-9 p-0 sm:w-auto sm:px-3 text-destructive hover:text-destructive hover:bg-destructive/10"
                      >
                        {loadingStates[automation.id] ? (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                          <Trash2 className="h-4 w-4" />
                        )}
                        <span className="hidden sm:inline ml-2">Delete</span>
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })
        )}
      </div>

      {/* Campaign Creation Modal */}
      <CreateCampaignModal
        open={isCreateCampaignOpen}
        onClose={() => setIsCreateCampaignOpen(false)}
        onCreated={handleCampaignCreated}
      />

      {/* Floating Action Button for Mobile */}
      <Button
        size="lg"
        className="fixed bottom-6 right-6 h-14 w-14 rounded-full shadow-xl hover:shadow-2xl lg:hidden"
        onClick={() => setIsCreateCampaignOpen(true)}
      >
        <Plus className="h-6 w-6" />
      </Button>
    </div>
  );
};

export default Automations;