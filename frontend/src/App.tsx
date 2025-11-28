import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Routes, Route, Outlet, Navigate } from "react-router-dom";
import { SidebarProvider } from "@/components/ui/sidebar";
import { AppSidebar } from "./components/AppSidebar";
import { Header } from "./components/Header";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { AdminRoute } from "./components/AdminRoute";
import Dashboard from "./pages/Dashboard";
import Campaigns from "./pages/Campaigns";
import Contacts from "./pages/Contacts";
import Automations from "./pages/Automations";
import Reports from "./pages/Reports";
import NotFound from "./pages/NotFound";
import Login from "@/pages/Login";
import Settings from "@/pages/Settings";
import Profile from "@/pages/Profile";
import ActiveCampaigns from "@/pages/ActiveCampaigns";
import { useAuthStore } from "@/store/authStore";

const queryClient = new QueryClient();

const AppLayout = () => {
  return (
    <div className="flex min-h-screen w-full">
      <AppSidebar />
      <div className="flex-1 flex flex-col w-full">
        <Header />
        <main className="flex-1">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

const App = () => {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <SidebarProvider>
          <Routes>
            {/* Public routes (no layout) */}
            <Route 
              path="/login" 
              element={isAuthenticated ? <Navigate to="/" replace /> : <Login />} 
            />

            {/* Protected routes with AppLayout */}
            <Route
              element={
                <ProtectedRoute>
                  <AppLayout />
                </ProtectedRoute>
              }
            >
              <Route path="/" element={<Dashboard />} />
              <Route path="/campaigns" element={<Campaigns />} />
              <Route path="/active-campaigns" element={<ActiveCampaigns />} />
              <Route path="/contacts" element={<Contacts />} />
              <Route path="/automations" element={<Automations />} />
              <Route path="/reports" element={<Reports />} />
              <Route
                path="/settings"
                element={
                  <AdminRoute>
                    <Settings />
                  </AdminRoute>
                }
              />
              <Route path="/profile" element={<Profile />} />
              {/* 404 catch-all route */}
              <Route path="*" element={<NotFound />} />
            </Route>
          </Routes>
        </SidebarProvider>
      </TooltipProvider>
    </QueryClientProvider>
  );
};

export default App;


// import { useState } from "react";

// function App() {
//   const [selectedFile, setSelectedFile] = useState<File | null>(null);
//   const [uploading, setUploading] = useState(false);
//   const [message, setMessage] = useState("");
//   const [fileInfo, setFileInfo] = useState("");
//   const [rawResponse, setRawResponse] = useState("");

//   const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
//     if (e.target.files && e.target.files.length > 0) {
//       const file = e.target.files[0];
//       const fileExt = file.name.split('.').pop()?.toLowerCase();
      
//       const allowedExtensions = ['csv', 'xlsx', 'xls'];
//       if (!fileExt || !allowedExtensions.includes(fileExt)) {
//         alert(`Invalid file type: .${fileExt}. Please upload CSV or Excel files only.`);
//         e.target.value = "";
//         setSelectedFile(null);
//         setFileInfo("");
//         return;
//       }
      
//       const maxSize = 50 * 1024 * 1024;
//       if (file.size > maxSize) {
//         alert(`File size too large: ${(file.size / (1024 * 1024)).toFixed(2)}MB. Maximum allowed: 50MB`);
//         e.target.value = "";
//         setSelectedFile(null);
//         setFileInfo("");
//         return;
//       }
      
//       if (file.size > 10 * 1024 * 1024) {
//         setFileInfo(`Large file selected: ${file.name} (${(file.size / (1024 * 1024)).toFixed(2)}MB) - Upload may take several minutes`);
//       } else {
//         setFileInfo(`File selected: ${file.name} (${(file.size / (1024 * 1024)).toFixed(2)}MB)`);
//       }
      
//       setSelectedFile(file);
//       setRawResponse(""); // Clear previous response
//     }
//   };

//   const testServerConnection = async () => {
//     try {
//       setMessage("Testing server connection...");
//       const response = await fetch("http://127.0.0.1:8000/api/contacts/", {
//         method: "GET",
//       });
      
//       const text = await response.text();
//       setRawResponse(text);
      
//       if (response.ok) {
//         setMessage("✅ Server is responding correctly");
//       } else {
//         setMessage(`❌ Server error: ${response.status} ${response.statusText}`);
//       }
//     } catch (error) {
//       setMessage(`❌ Cannot connect to server: ${error.message}`);
//     }
//   };

//   const uploadFile = async () => {
//     if (!selectedFile) {
//       alert("Please select a file.");
//       return;
//     }

//     setUploading(true);
//     setMessage("Uploading... This may take several minutes for large files.");
//     setRawResponse("");
    
//     const formData = new FormData();
//     formData.append("file", selectedFile);

//     try {
//       const controller = new AbortController();
//       const timeoutId = setTimeout(() => controller.abort(), 15 * 60 * 1000);

//       console.log("Starting upload...", selectedFile.name, selectedFile.size);

//       const response = await fetch("http://127.0.0.1:8000/api/contacts/upload/", {
//         method: "POST",
//         body: formData,
//         signal: controller.signal,
//       });

//       clearTimeout(timeoutId);

//       // Get raw response text first
//       const responseText = await response.text();
//       setRawResponse(responseText);
//       console.log("Raw server response:", responseText);

//       let result;
//       try {
//         result = JSON.parse(responseText);
//       } catch (jsonError) {
//         console.error("JSON parse error:", jsonError);
//         setMessage(`❌ Server returned HTML instead of JSON. This usually means a server error.\n\nCheck:\n1. Django server is running\n2. URL is correct\n3. Backend has no syntax errors`);
//         return;
//       }

//       setUploading(false);

//       if (response.ok) {
//         const newContacts = result.inserted !== undefined ? result.inserted : (result.unique || 0);
//         const updatedContacts = result.updated || 0;
        
//         if (newContacts === 0 && updatedContacts === 0) {
//           setMessage(`⚠️ No contacts processed.\n\nServer response: ${JSON.stringify(result, null, 2)}`);
//         } else {
//           setMessage(`✅ Uploaded Successfully! ${newContacts} new contacts added, ${updatedContacts} updated`);
//         }
//       } else {
//         const errorMsg = result.error || result.detail || 'Upload failed';
//         setMessage(`❌ Error: ${errorMsg}`);
//       }
//     } catch (error) {
//       setUploading(false);
//       console.error("Upload error:", error);
      
//       if (error.name === 'AbortError') {
//         setMessage("⏰ Upload timeout! The file is too large or server is taking too long to respond.");
//       } else if (error.message.includes('Failed to fetch')) {
//         setMessage("🌐 Network error! Check if the server is running and accessible.");
//       } else {
//         setMessage(`❌ Upload failed: ${error.message}`);
//       }
//     }
//   };

//   const debugFileStructure = async () => {
//     if (!selectedFile) {
//       alert("Please select a file first.");
//       return;
//     }

//     setUploading(true);
//     setMessage("Analyzing file structure...");
//     setRawResponse("");
    
//     const formData = new FormData();
//     formData.append("file", selectedFile);

//     try {
//       const response = await fetch("http://127.0.0.1:8000/api/contacts/debug-upload/", {
//         method: "POST",
//         body: formData,
//       });

//       const responseText = await response.text();
//       setRawResponse(responseText);

//       if (response.ok) {
//         const result = JSON.parse(responseText);
//         console.log("Debug result:", result);
//         setMessage(`🔍 File Analysis Complete!\nCheck browser console (F12) for details.`);
//       } else {
//         setMessage(`❌ Debug failed: Server returned ${response.status}`);
//       }
//     } catch (error) {
//       setMessage(`❌ Debug error: ${error.message}`);
//     } finally {
//       setUploading(false);
//     }
//   };

//   return (
//     <div style={{ padding: "40px", maxWidth: "800px", margin: "auto" }}>
//       <h2>Contact Data Upload - Debug Mode</h2>
      
//       <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
//         <button
//           onClick={testServerConnection}
//           style={{
//             padding: "10px 15px",
//             background: "#ff9800",
//             border: "none",
//             color: "#fff",
//             borderRadius: "4px",
//             cursor: "pointer"
//           }}
//         >
//           🔌 Test Server
//         </button>
        
//         <div style={{ flex: 1, color: '#666', fontSize: '14px' }}>
//           Supported formats: CSV, Excel (.xlsx, .xls) - Max 50MB
//         </div>
//       </div>

//       <input
//         type="file"
//         accept=".csv,.xlsx,.xls"
//         onChange={handleFileChange}
//         style={{
//           marginTop: "20px",
//           marginBottom: "10px",
//           padding: "10px",
//           width: "100%",
//           border: "2px dashed #ccc",
//           borderRadius: "5px"
//         }}
//       />

//       {fileInfo && (
//         <p style={{ 
//           marginBottom: "20px", 
//           padding: "8px", 
//           background: "#f0f8ff", 
//           borderRadius: "4px",
//           fontSize: "14px",
//           border: "1px solid #d1ecf1"
//         }}>
//           📁 {fileInfo}
//         </p>
//       )}

//       <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
//         <button
//           onClick={uploadFile}
//           disabled={uploading || !selectedFile}
//           style={{
//             padding: "12px 24px",
//             background: uploading ? "#aaa" : (selectedFile ? "#4CAF50" : "#ccc"),
//             border: "none",
//             color: "#fff",
//             cursor: (uploading || !selectedFile) ? "not-allowed" : "pointer",
//             borderRadius: "6px",
//             flex: 2,
//             fontSize: "16px",
//             fontWeight: "bold"
//           }}
//         >
//           {uploading ? "⏳ Uploading..." : "📤 Upload File"}
//         </button>

//         <button
//           onClick={debugFileStructure}
//           disabled={uploading || !selectedFile}
//           style={{
//             padding: "12px 16px",
//             background: !selectedFile ? "#ccc" : "#2196F3",
//             border: "none",
//             color: "#fff",
//             cursor: (uploading || !selectedFile) ? "not-allowed" : "pointer",
//             borderRadius: "6px",
//             flex: 1,
//             fontSize: "14px",
//           }}
//         >
//           🔍 Debug File
//         </button>
//       </div>

//       {message && (
//         <div
//           style={{
//             marginTop: "20px",
//             padding: "15px",
//             background: message.includes("❌") ? "#ffebee" : 
//                        message.includes("✅") ? "#e8f5e8" : 
//                        message.includes("⚠️") ? "#fff3cd" : "#f3e5f5",
//             borderRadius: "8px",
//             border: message.includes("❌") ? "1px solid #f44336" : 
//                    message.includes("✅") ? "1px solid #4CAF50" : 
//                    message.includes("⚠️") ? "1px solid #ff9800" : "1px solid #9c27b0",
//             whiteSpace: 'pre-line',
//             fontSize: '14px'
//           }}
//         >
//           {message}
//         </div>
//       )}

//       {rawResponse && (
//         <div style={{ marginTop: '20px' }}>
//           <h4>Raw Server Response:</h4>
//           <pre style={{
//             background: '#f5f5f5',
//             padding: '15px',
//             borderRadius: '5px',
//             border: '1px solid #ddd',
//             maxHeight: '300px',
//             overflow: 'auto',
//             fontSize: '12px'
//           }}>
//             {rawResponse.substring(0, 2000)}...
//           </pre>
//         </div>
//       )}

//       {/* Help section */}
//       <div style={{ marginTop: '30px', padding: '15px', background: '#f5f5f5', borderRadius: '5px' }}>
//         <h4 style={{ margin: '0 0 10px 0' }}>🔧 Troubleshooting Steps:</h4>
//         <ol style={{ margin: 0, paddingLeft: '20px', fontSize: '13px' }}>
//           <li>Click "Test Server" to check if backend is running</li>
//           <li>Check Django terminal for error messages</li>
//           <li>Verify the upload URL in Django urls.py</li>
//           <li>Check if CORS is configured in Django settings</li>
//           <li>Look for Python syntax errors in your views.py</li>
//         </ol>
//       </div>
//     </div>
//   );
// }

// export default App;