# Conversation History System

## Overview
The GPUStack UI now includes a comprehensive conversation history system that allows users to save, manage, and retrieve their chat conversations. This feature provides persistent storage of all user interactions with the AI models.

## Features

### 🗣️ Conversation Management
- **Create New Conversations**: Start fresh conversations with a dedicated button
- **Load Previous Conversations**: Click on any conversation to resume where you left off
- **Delete Conversations**: Remove conversations with confirmation dialog
- **Auto-Save**: Messages are automatically saved to the active conversation

### 🔍 Search & Discovery
- **Search Conversations**: Find conversations by title or message content
- **Real-time Filtering**: Search results update as you type
- **Smart Sorting**: Conversations ordered by most recent activity

### 📊 Statistics & Overview
- **Conversation Count**: Total number of conversations
- **Message Count**: Total messages across all conversations
- **Recent Activity**: Track your chat activity

### 🎨 User Interface
- **Collapsible Sidebar**: Toggle conversation history on/off
- **Visual Indicators**: Active conversation highlighting
- **Responsive Design**: Clean, modern interface
- **Hover Effects**: Interactive conversation items

## How to Use

### Access Conversation History
1. Click the "🗣️ History" button in the chat header
2. The conversation sidebar will slide out from the left
3. Use "✕" or click "Hide History" to close the sidebar

### Create a New Conversation
1. Open the conversation history sidebar
2. Click the "+ New Chat" button
3. A new conversation will be created and activated
4. Start chatting - messages will be saved automatically

### Load an Existing Conversation
1. Open the conversation history sidebar
2. Browse your conversation list
3. Click on any conversation to load it
4. All previous messages will be restored
5. Continue the conversation where you left off

### Search Conversations
1. Use the search box at the top of the conversation sidebar
2. Type keywords from conversation titles or message content
3. Results filter in real-time
4. Clear the search to show all conversations

### Delete Conversations
1. Hover over a conversation in the list
2. Click the "🗑️" delete button
3. Confirm deletion in the dialog
4. Conversation and all messages will be permanently removed

## Technical Implementation

### Backend API Endpoints
- `GET /api/conversations/` - List user conversations
- `POST /api/conversations/` - Create new conversation
- `GET /api/conversations/{id}` - Get conversation with messages
- `PUT /api/conversations/{id}` - Update conversation
- `DELETE /api/conversations/{id}` - Delete conversation
- `POST /api/conversations/{id}/messages` - Add message
- `GET /api/conversations/search` - Search conversations
- `GET /api/conversations/stats` - Get user statistics

### Database Schema
- **Conversations Table**: Stores conversation metadata
- **Messages Table**: Stores individual messages with metadata
- **User Isolation**: Each user can only access their own conversations
- **UUID Primary Keys**: Secure, unique identifiers

### Frontend Integration
- **Auto-Save**: Messages automatically saved after AI responses
- **State Management**: Current conversation ID tracking
- **Context Rebuilding**: Conversation context restored when loading
- **Real-time Updates**: Conversation list refreshes after changes

## Authentication Required
All conversation history features require user authentication. Users must log in to:
- Create and save conversations
- Access conversation history
- Search through conversations
- View conversation statistics

## Data Privacy
- **User Isolation**: Users can only see their own conversations
- **Secure Storage**: All data stored with proper authentication checks
- **Permanent Deletion**: Deleted conversations cannot be recovered

## Performance Features
- **Pagination**: Large conversation lists are paginated for performance
- **Efficient Search**: Full-text search across titles and content
- **Lazy Loading**: Messages loaded only when conversation is opened
- **Context Window Management**: AI context properly managed for large conversations

## Future Enhancements
- **Conversation Tags**: Organize conversations with custom tags
- **Export/Import**: Bulk export and import of conversation data
- **Sharing**: Share conversations with other users
- **Conversation Templates**: Save and reuse conversation starters
- **Advanced Search**: Date ranges, model filters, and more search options

## Troubleshooting

### Conversations Not Saving
- Ensure you're logged in with valid credentials
- Check that the conversation history sidebar is accessible
- Verify backend connectivity in browser console

### Search Not Working
- Clear the search box and try again
- Check network connectivity
- Ensure you're logged in

### Messages Not Loading
- Try refreshing the page
- Check browser console for errors
- Verify conversation still exists (may have been deleted)

---

The conversation history system provides a complete persistent chat experience, making the GPUStack UI suitable for long-term use and knowledge building across multiple sessions.
