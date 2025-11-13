import React, { useState, useEffect } from 'react';
import { Upload, Download, Trash2, Star, Clock, Users, HardDrive, FolderPlus, File, Folder, MoreVertical, Search, Grid, List, X, Settings, HelpCircle, Menu, ChevronRight } from 'lucide-react';

const GoogleDriveClone = () => {
  const [files, setFiles] = useState([]);
  const [folders, setFolders] = useState([]);
  const [currentView, setCurrentView] = useState('myDrive');
  const [searchQuery, setSearchQuery] = useState('');
  const [viewMode, setViewMode] = useState('list');
  const [showNewMenu, setShowNewMenu] = useState(false);
  const [selectedItems, setSelectedItems] = useState([]);
  const [currentFolder, setCurrentFolder] = useState(null);
  const [storageUsed, setStorageUsed] = useState(0);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const filesData = await window.storage.get('drive_files');
      const foldersData = await window.storage.get('drive_folders');
      
      if (filesData) setFiles(JSON.parse(filesData.value));
      if (foldersData) setFolders(JSON.parse(foldersData.value));
      
      calculateStorage();
    } catch (error) {
      console.log('No existing data');
    }
  };

  const saveData = async (newFiles, newFolders) => {
    await window.storage.set('drive_files', JSON.stringify(newFiles));
    await window.storage.set('drive_folders', JSON.stringify(newFolders));
    calculateStorage();
  };

  const calculateStorage = () => {
    const total = files.reduce((acc, file) => acc + (file.size || 0), 0);
    setStorageUsed(total);
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  const handleFileUpload = (e) => {
    const uploadedFiles = Array.from(e.target.files);
    const newFiles = uploadedFiles.map(file => ({
      id: Date.now() + Math.random(),
      name: file.name,
      size: file.size,
      type: file.type,
      owner: 'me',
      location: currentFolder || 'My Drive',
      dateModified: new Date().toISOString(),
      starred: false,
      shared: false
    }));

    const updatedFiles = [...files, ...newFiles];
    setFiles(updatedFiles);
    saveData(updatedFiles, folders);
  };

  const createFolder = () => {
    const folderName = prompt('Enter folder name:');
    if (folderName) {
      const newFolder = {
        id: Date.now(),
        name: folderName,
        parent: currentFolder,
        dateCreated: new Date().toISOString(),
        starred: false
      };
      const updatedFolders = [...folders, newFolder];
      setFolders(updatedFolders);
      saveData(files, updatedFolders);
    }
  };

  const deleteItem = (id, isFolder) => {
    if (window.confirm('Are you sure you want to delete this item?')) {
      if (isFolder) {
        const updatedFolders = folders.filter(f => f.id !== id);
        setFolders(updatedFolders);
        saveData(files, updatedFolders);
      } else {
        const updatedFiles = files.filter(f => f.id !== id);
        setFiles(updatedFiles);
        saveData(updatedFiles, folders);
      }
    }
  };

  const toggleStar = (id, isFolder) => {
    if (isFolder) {
      const updatedFolders = folders.map(f => 
        f.id === id ? { ...f, starred: !f.starred } : f
      );
      setFolders(updatedFolders);
      saveData(files, updatedFolders);
    } else {
      const updatedFiles = files.map(f => 
        f.id === id ? { ...f, starred: !f.starred } : f
      );
      setFiles(updatedFiles);
      saveData(updatedFiles, folders);
    }
  };

  const downloadFile = (file) => {
    alert(`Downloading: ${file.name}`);
  };

  const getFilteredItems = () => {
    let filteredFiles = files;
    let filteredFolders = folders;

    if (searchQuery) {
      filteredFiles = files.filter(f => 
        f.name.toLowerCase().includes(searchQuery.toLowerCase())
      );
      filteredFolders = folders.filter(f => 
        f.name.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    switch (currentView) {
      case 'starred':
        filteredFiles = filteredFiles.filter(f => f.starred);
        filteredFolders = filteredFolders.filter(f => f.starred);
        break;
      case 'shared':
        filteredFiles = filteredFiles.filter(f => f.shared);
        break;
      case 'recent':
        filteredFiles = [...filteredFiles].sort((a, b) => 
          new Date(b.dateModified) - new Date(a.dateModified)
        ).slice(0, 20);
        break;
      case 'trash':
        filteredFiles = [];
        filteredFolders = [];
        break;
    }

    return { filteredFiles, filteredFolders };
  };

  const { filteredFiles, filteredFolders } = getFilteredItems();

  const SidebarItem = ({ icon: Icon, label, view, badge }) => (
    <button
      onClick={() => setCurrentView(view)}
      className={`w-full flex items-center gap-3 px-4 py-2 rounded-r-full transition-colors ${
        currentView === view ? 'bg-blue-100 text-blue-600' : 'hover:bg-gray-100'
      }`}
    >
      <Icon size={20} />
      <span className="flex-1 text-left">{label}</span>
      {badge && <span className="text-xs text-gray-500">{badge}</span>}
    </button>
  );

  return (
    <div className="h-screen flex flex-col bg-white">
      {/* Header */}
      <header className="flex items-center gap-4 px-4 py-2 border-b">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-gradient-to-br from-yellow-400 via-green-400 to-blue-400 rounded"></div>
            <span className="text-xl font-normal text-gray-700">Drive</span>
          </div>
        </div>

        <div className="flex-1 flex items-center max-w-3xl">
          <div className="flex items-center bg-gray-100 rounded-lg px-4 py-2 flex-1">
            <Search size={20} className="text-gray-500 mr-2" />
            <input
              type="text"
              placeholder="Search in Drive"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="bg-transparent flex-1 outline-none"
            />
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button className="p-2 hover:bg-gray-100 rounded-full">
            <HelpCircle size={20} className="text-gray-600" />
          </button>
          <button className="p-2 hover:bg-gray-100 rounded-full">
            <Settings size={20} className="text-gray-600" />
          </button>
          <button className="p-2 hover:bg-gray-100 rounded-full">
            <Menu size={20} className="text-gray-600" />
          </button>
          <div className="w-8 h-8 bg-orange-500 rounded-full flex items-center justify-center text-white font-medium">
            S
          </div>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <aside className="w-60 border-r flex flex-col">
          <div className="p-3 relative">
            <button
              onClick={() => setShowNewMenu(!showNewMenu)}
              className="flex items-center gap-3 px-6 py-3 rounded-2xl shadow-md hover:shadow-lg transition-shadow bg-white border"
            >
              <span className="text-2xl">+</span>
              <span className="font-medium">New</span>
            </button>
            
            {showNewMenu && (
              <div className="absolute top-full left-3 mt-2 bg-white shadow-lg rounded-lg py-2 w-56 z-10">
                <label className="flex items-center gap-3 px-4 py-2 hover:bg-gray-100 cursor-pointer">
                  <Upload size={18} />
                  <span>File upload</span>
                  <input
                    type="file"
                    multiple
                    onChange={handleFileUpload}
                    className="hidden"
                  />
                </label>
                <button
                  onClick={createFolder}
                  className="w-full flex items-center gap-3 px-4 py-2 hover:bg-gray-100"
                >
                  <FolderPlus size={18} />
                  <span>Folder</span>
                </button>
              </div>
            )}
          </div>

          <nav className="flex-1 py-2">
            <SidebarItem icon={HardDrive} label="My Drive" view="myDrive" />
            <SidebarItem icon={Users} label="Shared with me" view="shared" />
            <SidebarItem icon={Clock} label="Recent" view="recent" />
            <SidebarItem icon={Star} label="Starred" view="starred" />
            <SidebarItem icon={Trash2} label="Trash" view="trash" />
          </nav>

          <div className="p-4 border-t">
            <div className="text-sm text-gray-600 mb-2">
              {formatFileSize(storageUsed)} of 15 GB used
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full"
                style={{ width: `${(storageUsed / (15 * 1024 * 1024 * 1024)) * 100}%` }}
              ></div>
            </div>
            <button className="mt-3 text-sm text-blue-600 hover:bg-blue-50 px-3 py-1 rounded">
              Get more storage
            </button>
          </div>
        </aside>

        {/* Main Content */}
        <main className="flex-1 overflow-auto">
          <div className="p-6">
            <div className="flex items-center justify-between mb-6">
              <h1 className="text-2xl font-normal">
                {currentView === 'myDrive' && 'My Drive'}
                {currentView === 'shared' && 'Shared with me'}
                {currentView === 'recent' && 'Recent'}
                {currentView === 'starred' && 'Starred'}
                {currentView === 'trash' && 'Trash'}
              </h1>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setViewMode('list')}
                  className={`p-2 rounded ${viewMode === 'list' ? 'bg-gray-200' : 'hover:bg-gray-100'}`}
                >
                  <List size={20} />
                </button>
                <button
                  onClick={() => setViewMode('grid')}
                  className={`p-2 rounded ${viewMode === 'grid' ? 'bg-gray-200' : 'hover:bg-gray-100'}`}
                >
                  <Grid size={20} />
                </button>
              </div>
            </div>

            {/* Suggested Folders */}
            {currentView === 'myDrive' && (
              <div className="mb-8">
                <h2 className="text-sm font-medium text-gray-700 mb-3">Suggested folders</h2>
                <div className="grid grid-cols-3 gap-4">
                  {filteredFolders.slice(0, 3).map(folder => (
                    <div key={folder.id} className="flex items-center gap-3 p-3 border rounded-lg hover:bg-gray-50">
                      <Folder className="text-gray-500" size={20} />
                      <span className="flex-1 truncate">{folder.name}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Files List */}
            <div>
              <h2 className="text-sm font-medium text-gray-700 mb-3">
                {currentView === 'recent' ? 'Files' : 'Suggested files'}
              </h2>
              
              {viewMode === 'list' ? (
                <div className="border rounded-lg overflow-hidden">
                  <table className="w-full">
                    <thead className="bg-gray-50 border-b text-sm text-gray-700">
                      <tr>
                        <th className="text-left px-4 py-2 font-medium">Name</th>
                        <th className="text-left px-4 py-2 font-medium">Owner</th>
                        <th className="text-left px-4 py-2 font-medium">Last modified</th>
                        <th className="text-left px-4 py-2 font-medium">File size</th>
                        <th className="w-12"></th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredFolders.map(folder => (
                        <tr key={folder.id} className="border-b hover:bg-gray-50">
                          <td className="px-4 py-3 flex items-center gap-3">
                            <Folder className="text-gray-500" size={20} />
                            <span>{folder.name}</span>
                          </td>
                          <td className="px-4 py-3">me</td>
                          <td className="px-4 py-3 text-sm text-gray-600">
                            {new Date(folder.dateCreated).toLocaleDateString()}
                          </td>
                          <td className="px-4 py-3">—</td>
                          <td className="px-4 py-3">
                            <div className="flex items-center gap-2">
                              <button
                                onClick={() => toggleStar(folder.id, true)}
                                className="p-1 hover:bg-gray-200 rounded"
                              >
                                <Star size={16} className={folder.starred ? 'fill-yellow-400 text-yellow-400' : ''} />
                              </button>
                              <button
                                onClick={() => deleteItem(folder.id, true)}
                                className="p-1 hover:bg-gray-200 rounded"
                              >
                                <Trash2 size={16} />
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))}
                      {filteredFiles.map(file => (
                        <tr key={file.id} className="border-b hover:bg-gray-50">
                          <td className="px-4 py-3 flex items-center gap-3">
                            <File className="text-red-500" size={20} />
                            <span>{file.name}</span>
                          </td>
                          <td className="px-4 py-3">
                            <div className="flex items-center gap-2">
                              <div className="w-6 h-6 bg-orange-500 rounded-full flex items-center justify-center text-white text-xs">
                                S
                              </div>
                              <span>{file.owner}</span>
                            </div>
                          </td>
                          <td className="px-4 py-3 text-sm text-gray-600">
                            {new Date(file.dateModified).toLocaleDateString()}
                          </td>
                          <td className="px-4 py-3 text-sm text-gray-600">
                            {formatFileSize(file.size)}
                          </td>
                          <td className="px-4 py-3">
                            <div className="flex items-center gap-2">
                              <button
                                onClick={() => toggleStar(file.id, false)}
                                className="p-1 hover:bg-gray-200 rounded"
                              >
                                <Star size={16} className={file.starred ? 'fill-yellow-400 text-yellow-400' : ''} />
                              </button>
                              <button
                                onClick={() => downloadFile(file)}
                                className="p-1 hover:bg-gray-200 rounded"
                              >
                                <Download size={16} />
                              </button>
                              <button
                                onClick={() => deleteItem(file.id, false)}
                                className="p-1 hover:bg-gray-200 rounded"
                              >
                                <Trash2 size={16} />
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="grid grid-cols-4 gap-4">
                  {[...filteredFolders, ...filteredFiles].map(item => (
                    <div key={item.id} className="border rounded-lg p-4 hover:bg-gray-50">
                      {item.type ? (
                        <File className="text-red-500 mb-2" size={32} />
                      ) : (
                        <Folder className="text-gray-500 mb-2" size={32} />
                      )}
                      <p className="truncate font-medium">{item.name}</p>
                      <p className="text-xs text-gray-500 mt-1">
                        {item.size ? formatFileSize(item.size) : 'Folder'}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default GoogleDriveClone;