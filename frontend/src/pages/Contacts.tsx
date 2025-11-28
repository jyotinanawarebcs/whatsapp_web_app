// Contacts.tsx
import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Plus, Search, Upload, Download, Users, Tag, Trash2, FileText, X, Edit, Check, ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { contactsAPI } from "@/services/api";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from "@/components/ui/alert-dialog";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

interface Contact {
  id: number;
  name: string;
  phone: string;
  source_file: string | null;
  is_active: boolean;
  created_at: string;
}

interface ContactFile {
  filename: string;
  count: number;
}

interface PaginationInfo {
  current_page: number;
  total_pages: number;
  total_items: number;
  has_next: boolean;
  has_previous: boolean;
  page_size: number;
}

interface ContactsResponse {
  contacts: Contact[];
  pagination: PaginationInfo;
}

const Contacts = () => {
  const { toast } = useToast();
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [contactFiles, setContactFiles] = useState<ContactFile[]>([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(false);
  const [loadingFiles, setLoadingFiles] = useState(false);
  const [totalContacts, setTotalContacts] = useState(0);
  const [activeContacts, setActiveContacts] = useState(0);
  const [fileCount, setFileCount] = useState(0);
  
  // File contacts pagination states
  const [filePagination, setFilePagination] = useState<PaginationInfo>({
    current_page: 1,
    total_pages: 1,
    total_items: 0,
    has_next: false,
    has_previous: false,
    page_size: 10
  });
  const [filePageSize, setFilePageSize] = useState(10);

  // Pagination states
  const [pagination, setPagination] = useState<PaginationInfo>({
    current_page: 1,
    total_pages: 1,
    total_items: 0,
    has_next: false,
    has_previous: false,
    page_size: 10
  });
  const [pageSize, setPageSize] = useState(10);
  
  const [openUploadDialog, setOpenUploadDialog] = useState(false);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  
  const [openFileDialog, setOpenFileDialog] = useState(false);
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [fileContacts, setFileContacts] = useState<Contact[]>([]);
  const [loadingFileContacts, setLoadingFileContacts] = useState(false);
  
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false);
  const [fileToDelete, setFileToDelete] = useState<string | null>(null);
  
  const [editContact, setEditContact] = useState<Contact | null>(null);
  const [editedPhone, setEditedPhone] = useState("");

  // Fetch all contacts and files
  useEffect(() => {
    fetchContacts();
    fetchContactFiles();
  }, []);
  
  // Update statistics whenever contacts change
  useEffect(() => {
    setTotalContacts(pagination.total_items);
    setActiveContacts(contacts.filter(c => c.is_active).length);
  }, [contacts, pagination.total_items]);
  
  // Update file count when contactFiles changes
  useEffect(() => {
    setFileCount(contactFiles.length);
  }, [contactFiles]);

  // Fetch contacts with pagination
  const fetchContacts = async (page: number = 1, size: number = pageSize) => {
    try {
      setLoading(true);
      console.log(`Fetching contacts - Page: ${page}, Size: ${size}`);
      
      const data = await contactsAPI.getAll(page, size);
      console.log('Received data:', data);
      
      // Handle different response formats
      if (data.contacts && Array.isArray(data.contacts)) {
        setContacts(data.contacts);
        
        if (data.pagination) {
          setPagination(data.pagination);
          setTotalContacts(data.pagination.total_items);
        } else {
          // Fallback if no pagination data
          setPagination({
            current_page: page,
            total_pages: 1,
            total_items: data.contacts.length,
            has_next: false,
            has_previous: page > 1,
            page_size: size
          });
          setTotalContacts(data.contacts.length);
        }
        
        setActiveContacts(data.contacts.filter((c: Contact) => c.is_active).length);
      } else if (Array.isArray(data)) {
        // If API returns direct array without pagination
        setContacts(data);
        const totalItems = data.length;
        const totalPages = Math.ceil(totalItems / size);
        
        setPagination({
          current_page: page,
          total_pages: totalPages,
          total_items: totalItems,
          has_next: page < totalPages,
          has_previous: page > 1,
          page_size: size
        });
        setTotalContacts(totalItems);
        setActiveContacts(data.filter((c: Contact) => c.is_active).length);
      } else {
        // Empty state
        setContacts([]);
        setPagination({
          current_page: 1,
          total_pages: 1,
          total_items: 0,
          has_next: false,
          has_previous: false,
          page_size: size
        });
        setTotalContacts(0);
        setActiveContacts(0);
      }
      
    } catch (err: any) {
      console.error('Error fetching contacts:', err);
      toast({
        title: "Error fetching contacts",
        description: err.message || "Failed to load contact data.",
        variant: "destructive",
      });
      
      // Set empty state on error
      setContacts([]);
      setPagination({
        current_page: 1,
        total_pages: 1,
        total_items: 0,
        has_next: false,
        has_previous: false,
        page_size: pageSize
      });
      setTotalContacts(0);
      setActiveContacts(0);
    } finally {
      setLoading(false);
    }
  };
  
  const fetchContactFiles = async () => {
    try {
      setLoadingFiles(true);
      console.log('Fetching contact files...');
      
      const data = await contactsAPI.getFiles();
      
      if (Array.isArray(data)) {
        console.log(`Received ${data.length} contact files:`, data);
        setContactFiles(data);
        setFileCount(data.length);
      } else {
        console.error('Received invalid data format for contact files:', data);
        setContactFiles([]);
        setFileCount(0);
      }
    } catch (err: any) {
      console.error('Error fetching contact files:', err);
      toast({
        title: "Error fetching contact files",
        description: err.message || "Failed to load file data.",
        variant: "destructive",
      });
      setContactFiles([]);
      setFileCount(0);
    } finally {
      setLoadingFiles(false);
    }
  };
  
  const handlePageChange = (newPage: number) => {
    if (newPage >= 1 && newPage <= pagination.total_pages) {
      fetchContacts(newPage, pageSize);
    }
  };

  const handlePageSizeChange = (newSize: number) => {
    setPageSize(newSize);
    fetchContacts(1, newSize);
  };

  const handleUpload = async () => {
    if (!uploadFile) return;
    
    try {
      setUploading(true);
      
      // Check if file is a supported format
      const fileExt = uploadFile.name.split('.').pop()?.toLowerCase();
      if (!fileExt || !['csv', 'txt', 'xls', 'xlsx'].includes(fileExt)) {
        toast({
          title: "Invalid file type",
          description: "Please upload a CSV, TXT, XLS, or XLSX file.",
          variant: "destructive",
        });
        return;
      }
      
      // Check file size
      if (uploadFile.size > 100 * 1024 * 1024) {
        toast({
          title: "File too large",
          description: "Please upload a file smaller than 100MB.",
          variant: "destructive",
        });
        return;
      }
      
      const result = await contactsAPI.uploadFile(uploadFile);
      
      if (result.unique > 0) {
        toast({
          title: "File uploaded successfully",
          description: `Added ${result.unique} unique contacts from ${result.originalname}`,
        });
      } else {
        toast({
          title: "File processed",
          description: `No contacts found in ${result.originalname}. Please make sure your file contains phone numbers.`,
          variant: "destructive",
          duration: 6000,
        });
      }
      
      setOpenUploadDialog(false);
      setUploadFile(null);
      
      // Refresh data
      await fetchContacts(1, pageSize);
      await fetchContactFiles();
      
    } catch (err: any) {
      console.error('Upload error:', err);
      toast({
        title: "Upload failed",
        description: err.message || "There was an error uploading your file.",
        variant: "destructive",
      });
    } finally {
      setUploading(false);
    }
  };

  const handleViewFile = async (filename: string, page: number = 1, size: number = filePageSize) => {
    console.log(`Viewing file: ${filename}, Page: ${page}, Size: ${size}`);
    setSelectedFile(filename);
    setLoadingFileContacts(true);
    
    try {
      // Backend pagination ke saath API call karo
      const data = await contactsAPI.getContactsByFile(filename, page, size);
      console.log('Raw file contacts response:', data);
      
      let contactsArray: Contact[] = [];
      let paginationData: PaginationInfo | null = null;
      
      if (data.contacts && Array.isArray(data.contacts)) {
        // Backend se paginated data mila hai
        contactsArray = data.contacts;
        
        if (data.pagination) {
          // Backend pagination data use karo
          paginationData = data.pagination;
          console.log('Using backend pagination:', paginationData);
        }
      } else if (Array.isArray(data)) {
        // Fallback: Direct array mila (frontend pagination)
        contactsArray = data;
        const totalItems = data.length;
        const totalPages = Math.ceil(totalItems / size);
        
        paginationData = {
          current_page: page,
          total_pages: totalPages,
          total_items: totalItems,
          has_next: page < totalPages,
          has_previous: page > 1,
          page_size: size
        };
      } else if (data && typeof data === 'object') {
        // Try to extract contacts from different response formats
        if (Array.isArray(data.data)) contactsArray = data.data;
        else if (Array.isArray(data.results)) contactsArray = data.results;
        else if (Array.isArray(data.items)) contactsArray = data.items;
        
        // Extract pagination info if available
        if (data.pagination) {
          paginationData = data.pagination;
        } else if (data.total || data.total_items) {
          const totalItems = data.total || data.total_items || contactsArray.length;
          const totalPages = Math.ceil(totalItems / size);
          
          paginationData = {
            current_page: page,
            total_pages: totalPages,
            total_items: totalItems,
            has_next: page < totalPages,
            has_previous: page > 1,
            page_size: size
          };
        }
      }
      
      console.log(`Final contacts array:`, contactsArray);
      console.log(`Pagination data:`, paginationData);
      
      setFileContacts(contactsArray);
      
      if (paginationData) {
        setFilePagination(paginationData);
      } else {
        // Fallback agar koi pagination data nahi mila
        setFilePagination({
          current_page: page,
          total_pages: 1,
          total_items: contactsArray.length,
          has_next: false,
          has_previous: false,
          page_size: size
        });
      }
      
    } catch (err: any) {
      console.error(`Error loading contacts from file ${filename}:`, err);
      toast({
        title: "Error",
        description: err.message || "Failed to load contacts from file.",
        variant: "destructive",
      });
      setFileContacts([]);
      setFilePagination({
        current_page: 1,
        total_pages: 1,
        total_items: 0,
        has_next: false,
        has_previous: false,
        page_size: filePageSize
      });
    } finally {
      setLoadingFileContacts(false);
    }
  };

  // File contacts pagination handlers
  const handleFilePageChange = (newPage: number) => {
    if (newPage >= 1 && newPage <= filePagination.total_pages && selectedFile) {
      handleViewFile(selectedFile, newPage, filePageSize);
    }
  };

  const handleFilePageSizeChange = (newSize: number) => {
    setFilePageSize(newSize);
    if (selectedFile) {
      handleViewFile(selectedFile, 1, newSize);
    }
  };

  // File contacts page numbers generator
  const generateFilePageNumbers = () => {
    const pages = [];
    const totalPages = filePagination.total_pages;
    const currentPage = filePagination.current_page;
    
    if (totalPages <= 5) {
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      if (currentPage <= 3) {
        pages.push(1, 2, 3, 4, '...', totalPages);
      } else if (currentPage >= totalPages - 2) {
        pages.push(1, '...', totalPages - 3, totalPages - 2, totalPages - 1, totalPages);
      } else {
        pages.push(1, '...', currentPage - 1, currentPage, currentPage + 1, '...', totalPages);
      }
    }
    
    return pages;
  };

  const handleDeleteFile = async () => {
    if (!fileToDelete) return;
    
    try {
      setLoadingFiles(true);
      console.log(`Deleting file ${fileToDelete} and all associated contacts...`);
      
      const result = await contactsAPI.removeContactsByFile(fileToDelete);
      
      console.log(`Deletion result:`, result);
      
      toast({
        title: "File deleted",
        description: `All contacts from ${fileToDelete} have been removed.`,
      });
      
      setOpenDeleteDialog(false);
      setFileToDelete(null);
      setSelectedFile(null);
      setFileContacts([]);
      
      // Refresh data
      setTimeout(async () => {
        try {
          await fetchContacts(1, pageSize);
          await fetchContactFiles();
        } catch (refreshError) {
          console.error('Error refreshing data after deletion:', refreshError);
        } finally {
          setLoadingFiles(false);
        }
      }, 500);
    } catch (err: any) {
      console.error('Delete file error:', err);
      setLoadingFiles(false);
      toast({
        title: "Error",
        description: err.message || "Failed to delete contacts.",
        variant: "destructive",
      });
    }
  };

  const handleDeleteContact = async (id: number) => {
    try {
      console.log(`Deleting contact with ID: ${id}`);
      
      // Find the contact to be deleted to get its source_file
      const contactToDelete = contacts.find(c => c.id === id);
      const sourceFile = contactToDelete?.source_file;
      
      await contactsAPI.remove(id);
      
      toast({
        title: "Contact deleted",
        description: "Contact has been removed.",
      });
      
      // Refresh all data
      await fetchContacts(pagination.current_page, pageSize);
      
      // If we're viewing a specific file, refresh its contacts with current pagination
      if (selectedFile) {
        console.log(`Refreshing file contacts for: ${selectedFile}`);
        try {
          await handleViewFile(selectedFile, filePagination.current_page, filePageSize);
        } catch (refreshError) {
          console.error('Error refreshing file contacts:', refreshError);
        }
      }
      
      // If the deleted contact was from a file, refresh the file list
      if (sourceFile) {
        await fetchContactFiles();
      }
      
    } catch (err: any) {
      console.error('Delete contact error:', err);
      toast({
        title: "Error",
        description: err.message || "Failed to delete contact.",
        variant: "destructive",
      });
    }
  };

  const handleEditContact = async () => {
    if (!editContact) return;
    
    try {
      await contactsAPI.update(editContact.id, { 
        phone: editedPhone 
      });
      
      toast({
        title: "Contact updated",
        description: "Phone number has been updated.",
      });
      
      setEditContact(null);
      await fetchContacts(pagination.current_page, pageSize);
      
      if (selectedFile) {
        await handleViewFile(selectedFile, filePagination.current_page, filePageSize);
      }
    } catch (err: any) {
      toast({
        title: "Error",
        description: err.message || "Failed to update contact.",
        variant: "destructive",
      });
    }
  };

  const handleCreateContact = async () => {
    if (!editedPhone.trim()) {
      toast({
        title: "Error",
        description: "Please enter a phone number.",
        variant: "destructive",
      });
      return;
    }

    try {
      await contactsAPI.create({ phone: editedPhone });
      
      toast({
        title: "Contact created",
        description: "New contact has been added.",
      });
      
      setEditContact(null);
      setEditedPhone("");
      await fetchContacts(1, pageSize);
    } catch (err: any) {
      toast({
        title: "Error",
        description: err.message || "Failed to create contact.",
        variant: "destructive",
      });
    }
  };
  
  const filteredContacts = contacts.filter(contact => 
    contact.phone.toLowerCase().includes(search.toLowerCase()) ||
    (contact.name && contact.name.toLowerCase().includes(search.toLowerCase()))
  );

  // Generate page numbers for pagination
  const generatePageNumbers = () => {
    const pages = [];
    const totalPages = pagination.total_pages;
    const currentPage = pagination.current_page;
    
    if (totalPages <= 5) {
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      if (currentPage <= 3) {
        pages.push(1, 2, 3, 4, '...', totalPages);
      } else if (currentPage >= totalPages - 2) {
        pages.push(1, '...', totalPages - 3, totalPages - 2, totalPages - 1, totalPages);
      } else {
        pages.push(1, '...', currentPage - 1, currentPage, currentPage + 1, '...', totalPages);
      }
    }
    
    return pages;
  };

  return (
    <div className="p-4 sm:p-6 space-y-6">
        {/* Header Section */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Contacts</h1>
            <p className="mt-1 text-muted-foreground">Manage your contact lists</p>
          </div>
          <div className="flex gap-2">
            <Button 
              variant="outline" 
              className="flex-1 sm:flex-none"
              onClick={() => {
                setOpenFileDialog(true);
                fetchContactFiles();
              }}
            >
              <FileText className="h-4 w-4 mr-2" />
              Manage Files
            </Button>
            <Button 
              className="flex-1 sm:flex-none bg-primary hover:bg-primary/90"
              onClick={() => setOpenUploadDialog(true)}
            >
              <Upload className="h-4 w-4 mr-2" />
              Import
            </Button>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid gap-6 sm:grid-cols-3">
          <div className="rounded-lg border border-border bg-card p-6">
            <div className="flex items-center gap-4">
              <div className="rounded-lg bg-primary/10 p-3">
                <Users className="h-6 w-6 text-primary" />
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground">Total Contacts</p>
                <h3 className="text-2xl font-bold text-foreground">{totalContacts.toLocaleString()}</h3>
              </div>
            </div>
          </div>
          <div className="rounded-lg border border-border bg-card p-6">
            <div className="flex items-center gap-4">
              <div className="rounded-lg bg-success/10 p-3">
                <Users className="h-6 w-6 text-success" />
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground">Active Contacts</p>
                <h3 className="text-2xl font-bold text-foreground">{activeContacts.toLocaleString()}</h3>
              </div>
            </div>
          </div>
          <div className="rounded-lg border border-border bg-card p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="rounded-lg bg-warning/10 p-3">
                  <FileText className="h-6 w-6 text-warning" />
                </div>
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Contact Files</p>
                  <h3 className="text-2xl font-bold text-foreground">{fileCount}</h3>
                </div>
              </div>
              <button 
                className="text-muted-foreground hover:text-foreground p-1 rounded-full hover:bg-accent/50 transition-colors"
                onClick={fetchContactFiles}
                title="Refresh file count"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"></path><path d="M3 3v5h5"></path><path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16"></path><path d="M16 21h5v-5"></path></svg>
              </button>
            </div>
          </div>
        </div>

        {/* Search and Refresh */}
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Search contacts..."
              className="pl-9 bg-card border-border"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <Button 
            variant="outline" 
            className="w-full sm:w-auto"
            disabled={loading}
            onClick={() => fetchContacts(1, pageSize)}
          >
            <Users className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>

        {/* Contacts Table */}
        <div className="rounded-lg border border-border bg-card">
          <Table>
            <TableHeader>
              <TableRow className="hover:bg-transparent border-border">
                <TableHead>Name</TableHead>
                <TableHead>Phone Number</TableHead>
                <TableHead>Source File</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Added Date</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center py-8">
                    Loading contacts...
                  </TableCell>
                </TableRow>
              ) : filteredContacts.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center py-8">
                    {search ? "No contacts match your search." : "No contacts found."}
                  </TableCell>
                </TableRow>
              ) : (
                filteredContacts.map((contact) => (
                  <TableRow key={contact.id} className="border-border">
                    <TableCell>{contact.name || <i className="text-muted-foreground">N/A</i>}</TableCell>
                    <TableCell className="font-medium">{contact.phone}</TableCell>
                    <TableCell className="text-muted-foreground">
                      {contact.source_file ? (
                        <span className="flex items-center gap-1">
                          <FileText className="h-3 w-3" />
                          {contact.source_file}
                        </span>
                      ) : (
                        <span className="text-muted-foreground italic">Manual entry</span>
                      )}
                    </TableCell>
                    <TableCell>
                      <Badge variant={contact.is_active ? "default" : "secondary"} className={`text-xs ${contact.is_active ? "text-white" : ""}`}>
                        {contact.is_active ? "Active" : "Inactive"}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-muted-foreground">
                      {new Date(contact.created_at).toLocaleDateString()}
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-2">
                        <Button 
                          variant="ghost" 
                          size="sm"
                          onClick={() => {
                            setEditContact(contact);
                            setEditedPhone(contact.phone);
                          }}
                        >
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button 
                          variant="ghost" 
                          size="sm"
                          onClick={() => handleDeleteContact(contact.id)}
                        >
                          <Trash2 className="h-4 w-4 text-destructive" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>

        {/* Pagination Controls - Only show if there are multiple pages */}
        {pagination.total_pages > 1 && (
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 mt-6 py-4 border-t border-border">
            {/* Page Size Selector */}
            <div className="flex items-center gap-2">
              <Label htmlFor="page-size" className="text-sm text-muted-foreground whitespace-nowrap">
                Rows per page:
              </Label>
              <select
                id="page-size"
                value={pageSize}
                onChange={(e) => handlePageSizeChange(Number(e.target.value))}
                className="h-9 rounded-md border border-input bg-[#101729] text-white px-3 py-1 text-sm shadow-sm focus:outline-none focus:ring-1 focus:ring-ring"
              >
                <option value="5">5</option>
                <option value="10">10</option>
                <option value="20">20</option>
                <option value="50">50</option>
              </select>
            </div>

            {/* Page Info */}
            <div className="text-sm text-muted-foreground whitespace-nowrap">
              Page {pagination.current_page} of {pagination.total_pages} •{" "}
              {pagination.total_items.toLocaleString()} total contacts
            </div>

            {/* Pagination Buttons */}
            <div className="flex items-center gap-1">
              <Button
                variant="outline"
                size="sm"
                onClick={() => handlePageChange(1)}
                disabled={pagination.current_page === 1}
                className="hidden sm:flex h-9 w-9 p-0"
              >
                <ChevronsLeft className="h-4 w-4" />
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handlePageChange(pagination.current_page - 1)}
                disabled={!pagination.has_previous}
                className="h-9 w-9 p-0"
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              
              {/* Page Numbers */}
              <div className="flex items-center gap-1">
                {generatePageNumbers().map((pageNum, index) => (
                  pageNum === '...' ? (
                    <span key={`ellipsis-${index}`} className="px-2 text-muted-foreground">
                      ...
                    </span>
                  ) : (
                    <Button
                      key={pageNum}
                      variant={pagination.current_page === pageNum ? "default" : "outline"}
                      size="sm"
                      onClick={() => handlePageChange(pageNum as number)}
                      className="h-9 w-9 p-0"
                    >
                      {pageNum}
                    </Button>
                  )
                ))}
              </div>

              <Button
                variant="outline"
                size="sm"
                onClick={() => handlePageChange(pagination.current_page + 1)}
                disabled={!pagination.has_next}
                className="h-9 w-9 p-0"
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handlePageChange(pagination.total_pages)}
                disabled={pagination.current_page === pagination.total_pages}
                className="hidden sm:flex h-9 w-9 p-0"
              >
                <ChevronsRight className="h-4 w-4" />
              </Button>
            </div>
          </div>
        )}

      {/* Add Contact Button */}
      <Button
        size="lg"
        className="fixed bottom-6 right-6 h-14 w-14 rounded-full shadow-xl hover:shadow-2xl"
        onClick={() => {
          setEditContact(null);
          setEditedPhone("");
        }}
      >
        <Plus className="h-6 w-6" />
      </Button>

      {/* Upload Dialog */}
      <Dialog open={openUploadDialog} onOpenChange={setOpenUploadDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Import Contacts</DialogTitle>
            <DialogDescription>
              Upload a file with contact information (CSV, TXT, XLS, XLSX).
              The file should have a column with phone numbers or have phone numbers in the first column.
            </DialogDescription>
          </DialogHeader>
          
          <div className="grid gap-4 py-4">
            <Label htmlFor="contacts-file">Contact File</Label>
            <Input 
              id="contacts-file" 
              type="file" 
              accept=".csv,.txt,.xls,.xlsx" 
              onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
            />
            {uploadFile && (
              <p className="text-sm text-muted-foreground">
                Selected file: {uploadFile.name} ({Math.round(uploadFile.size / 1024)} KB)
              </p>
            )}
          </div>
          
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setOpenUploadDialog(false)}>Cancel</Button>
            <Button 
              onClick={handleUpload} 
              disabled={!uploadFile || uploading}
            >
              {uploading ? "Uploading..." : "Upload"}
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Manage Files Dialog */}
      <Dialog open={openFileDialog} onOpenChange={setOpenFileDialog}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
          <DialogHeader>
            <div className="flex justify-between items-center">
              <div>
                <DialogTitle>Manage Contact Files</DialogTitle>
                <DialogDescription>
                  View and manage your uploaded contact files.
                </DialogDescription>
              </div>
              <Button 
                variant="outline" 
                size="sm" 
                onClick={fetchContactFiles}
                disabled={loadingFiles}
              >
                {loadingFiles ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary mr-1"></div>
                    Refreshing...
                  </>
                ) : (
                  <>
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="mr-1"><path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"></path><path d="M3 3v5h5"></path><path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16"></path><path d="M16 21h5v-5"></path></svg>
                    Refresh Files
                  </>
                )}
              </Button>
            </div>
          </DialogHeader>
          
          <div className="py-4 flex-1 overflow-auto">
            {selectedFile ? (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <FileText className="h-5 w-5" />
                    <h3 className="font-medium">{selectedFile}</h3>
                    <Badge variant="outline">{filePagination.total_items.toLocaleString()} contacts</Badge>
                  </div>
                  <Button variant="ghost" size="sm" onClick={() => {
                    setSelectedFile(null);
                    setFileContacts([]);
                  }}>
                    <X className="h-4 w-4" />
                    Close
                  </Button>
                </div>
                
                <div className="border rounded-md overflow-hidden">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Phone Number</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead>Added Date</TableHead>
                        <TableHead className="text-right">Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {loadingFileContacts ? (
                        <TableRow>
                          <TableCell colSpan={4} className="text-center py-8">
                            <div className="flex flex-col items-center gap-2">
                              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
                              <p className="text-muted-foreground">Loading contacts...</p>
                            </div>
                          </TableCell>
                        </TableRow>
                      ) : fileContacts.length === 0 ? (
                        <TableRow>
                          <TableCell colSpan={4} className="text-center py-4">
                            No contacts found in this file.
                          </TableCell>
                        </TableRow>
                      ) : (
                        fileContacts.map((contact) => (
                          <TableRow key={contact.id}>
                            <TableCell className="font-medium">{contact.phone}</TableCell>
                            <TableCell>
                              <Badge variant={contact.is_active ? "default" : "secondary"} className="text-xs">
                                {contact.is_active ? "Active" : "Inactive"}
                              </Badge>
                            </TableCell>
                            <TableCell className="text-muted-foreground">
                              {new Date(contact.created_at).toLocaleDateString()}
                            </TableCell>
                            <TableCell className="text-right">
                              <Button 
                                variant="ghost" 
                                size="sm"
                                onClick={() => handleDeleteContact(contact.id)}
                              >
                                <Trash2 className="h-4 w-4 text-destructive" />
                              </Button>
                            </TableCell>
                          </TableRow>
                        ))
                      )}
                    </TableBody>
                  </Table>
                </div>
                
                {/* FILE CONTACTS PAGINATION */}
                {filePagination.total_pages > 1 && (
                  <div className="flex flex-col sm:flex-row items-center justify-between gap-4 mt-4 py-4 border-t border-border">
                    {/* Page Size Selector */}
                    <div className="flex items-center gap-2">
                      <Label htmlFor="file-page-size" className="text-sm text-muted-foreground whitespace-nowrap">
                        Rows per page:
                      </Label>
                      <select
                        id="file-page-size"
                        value={filePageSize}
                        onChange={(e) => handleFilePageSizeChange(Number(e.target.value))}
                        className="h-9 rounded-md border border-input bg-[#101729] text-white px-3 py-1 text-sm shadow-sm focus:outline-none focus:ring-1 focus:ring-ring"
                      >
                        <option value="5">5</option>
                        <option value="10">10</option>
                        <option value="20">20</option>
                        <option value="50">50</option>
                      </select>
                    </div>

                    {/* Page Info */}
                    <div className="text-sm text-muted-foreground whitespace-nowrap">
                      Page {filePagination.current_page} of {filePagination.total_pages} •{" "}
                      {filePagination.total_items.toLocaleString()} contacts
                    </div>

                    {/* Pagination Buttons */}
                    <div className="flex items-center gap-1">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleFilePageChange(1)}
                        disabled={filePagination.current_page === 1}
                        className="h-9 w-9 p-0"
                      >
                        <ChevronsLeft className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleFilePageChange(filePagination.current_page - 1)}
                        disabled={!filePagination.has_previous}
                        className="h-9 w-9 p-0"
                      >
                        <ChevronLeft className="h-4 w-4" />
                      </Button>
                      
                      {/* Page Numbers */}
                      <div className="flex items-center gap-1">
                        {generateFilePageNumbers().map((pageNum, index) => (
                          pageNum === '...' ? (
                            <span key={`file-ellipsis-${index}`} className="px-2 text-muted-foreground">
                              ...
                            </span>
                          ) : (
                            <Button
                              key={pageNum}
                              variant={filePagination.current_page === pageNum ? "default" : "outline"}
                              size="sm"
                              onClick={() => handleFilePageChange(pageNum as number)}
                              className="h-9 w-9 p-0"
                            >
                              {pageNum}
                            </Button>
                          )
                        ))}
                      </div>

                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleFilePageChange(filePagination.current_page + 1)}
                        disabled={!filePagination.has_next}
                        className="h-9 w-9 p-0"
                      >
                        <ChevronRight className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleFilePageChange(filePagination.total_pages)}
                        disabled={filePagination.current_page === filePagination.total_pages}
                        className="h-9 w-9 p-0"
                      >
                        <ChevronsRight className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                )}

                <div className="flex justify-between pt-4">
                  <Button 
                    variant="destructive" 
                    onClick={() => {
                      setFileToDelete(selectedFile);
                      setOpenDeleteDialog(true);
                    }}
                  >
                    <Trash2 className="h-4 w-4 mr-2" />
                    Delete All Contacts
                  </Button>
                  <Button variant="outline" onClick={() => {
                    setSelectedFile(null);
                    setFileContacts([]);
                  }}>Back to Files</Button>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                {loadingFiles ? (
                  <div className="text-center py-8">
                    <div className="flex flex-col items-center gap-2">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                      <p className="text-muted-foreground">Loading contact files...</p>
                    </div>
                  </div>
                ) : contactFiles.length === 0 ? (
                  <div className="text-center py-8">
                    <p className="text-muted-foreground">No contact files found.</p>
                    <div className="flex flex-col gap-2 mt-4 items-center">
                      <Button 
                        variant="outline"
                        onClick={() => {
                          setOpenFileDialog(false);
                          setOpenUploadDialog(true);
                        }}
                      >
                        <Upload className="h-4 w-4 mr-2" />
                        Upload Contacts
                      </Button>
                    </div>
                  </div>
                ) : (
                  <div className="grid gap-4 sm:grid-cols-2">
                    {contactFiles.map((file) => (
                      <div 
                        key={file.filename} 
                        className="border rounded-lg p-4 flex justify-between items-center hover:bg-accent/50 cursor-pointer transition-colors"
                        onClick={() => handleViewFile(file.filename)}
                      >
                        <div className="flex items-center gap-3">
                          <FileText className="h-8 w-8 text-primary" />
                          <div>
                            <p className="font-medium text-sm">{file.filename}</p>
                            <p className="text-sm text-muted-foreground">{file.count.toLocaleString()} contacts</p>
                          </div>
                        </div>
                        <Button variant="ghost" size="sm">
                          View
                        </Button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={openDeleteDialog} onOpenChange={setOpenDeleteDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
            <AlertDialogDescription>
              This will permanently delete all contacts from the file "{fileToDelete}".
              This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleDeleteFile}>Delete</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Edit/Create Contact Dialog */}
      <Dialog open={!!editContact} onOpenChange={(open) => !open && setEditContact(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{editContact ? "Edit Contact" : "Add Contact"}</DialogTitle>
          </DialogHeader>
          
          <div className="grid gap-4 py-4">
            <div>
              <Label htmlFor="phone-number">Phone Number</Label>
              <Input 
                id="phone-number" 
                value={editedPhone} 
                onChange={(e) => setEditedPhone(e.target.value)}
                placeholder="+1234567890"
              />
            </div>
          </div>
          
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setEditContact(null)}>Cancel</Button>
            <Button onClick={editContact ? handleEditContact : handleCreateContact}>
              <Check className="h-4 w-4 mr-2" />
              {editContact ? "Save" : "Create"}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default Contacts;