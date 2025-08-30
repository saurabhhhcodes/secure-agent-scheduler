# Global MCP Hackathon - Demo Guide

## 🚀 Quick Demo Script

### 1. **Welcome Page**
```bash
# Show the landing page
curl http://localhost:8000/
# Or visit in browser: http://localhost:8000/
```

### 2. **API Documentation** 
```bash
# Interactive docs
open http://localhost:8000/api/docs
```

### 3. **Health Check**
```bash
curl http://localhost:8000/api/health
```

### 4. **Core Feature Demo - Natural Language Scheduling**

#### Example 1: Basic Meeting
```bash
curl -X POST http://localhost:8000/api/schedule \
  -H "Content-Type: application/json" \
  -d '{
    "user_request": "Schedule a team meeting tomorrow at 2 PM for 1 hour",
    "user_id": "demo_user_001"
  }'
```

#### Example 2: Complex Scheduling
```bash
curl -X POST http://localhost:8000/api/schedule \
  -H "Content-Type: application/json" \
  -d '{
    "user_request": "Set up a client presentation next Friday at 10:30 AM for 90 minutes with reminder 15 minutes before",
    "user_id": "demo_user_002"
  }'
```

#### Example 3: Quick Appointment
```bash
curl -X POST http://localhost:8000/api/schedule \
  -H "Content-Type: application/json" \
  -d '{
    "user_request": "Doctor appointment Thursday 3 PM",
    "user_id": "demo_user_003"
  }'
```

### 5. **Audit Trail**
```bash
curl http://localhost:8000/api/audit?limit=10
```

## 🎯 Key Demo Points

### **Multi-Agent Architecture**
- **Planner Agent**: Parses natural language → structured events
- **Notifier Agent**: Handles secure notifications with OAuth
- **Orchestrator**: Coordinates agent workflow using LangGraph

### **Security Features**
- Descope OAuth token validation
- Scope-based permission checking
- Comprehensive audit logging
- Secure agent-to-agent communication

### **Natural Language Processing**
- Parses time expressions ("tomorrow at 2 PM")
- Extracts duration ("for 1 hour", "90 minutes")
- Identifies meeting types and titles
- Handles reminder preferences

### **Professional API**
- FastAPI with auto-generated docs
- Proper error handling and responses
- RESTful design patterns
- Comprehensive logging

## 🔧 Technical Architecture

```
Browser/Client → FastAPI → Orchestrator → [Planner Agent → Notifier Agent] → Response
                    ↓
                 Audit Log
```

## 🏆 Hackathon Submission Highlights

### **Innovation**
- Secure multi-agent communication using OAuth scopes
- Natural language to structured data conversion
- Real-time audit trail for compliance
- Extensible agent architecture

### **Technical Excellence**
- Clean, well-documented code
- Proper error handling and logging
- Security best practices
- Professional API design

### **Practical Value**
- Solves real scheduling coordination problems
- Enterprise-ready security model
- Extensible for multiple notification channels
- Clear audit trail for business compliance

## 📋 MCP Integration Opportunities

If MCP compliance is required, consider these additions:

1. **MCP Server Implementation**: Expose agents as MCP tools
2. **MCP Client Integration**: Connect to external MCP services
3. **Resource Sharing**: Implement MCP resource protocol
4. **Tool Discovery**: MCP-compliant tool registration

## 🎬 Demo Flow Recommendations

1. **Start**: Show landing page and architecture
2. **Core Demo**: Run 2-3 scheduling examples
3. **Show Results**: Display created events and notifications
4. **Security**: Explain OAuth and audit features
5. **Architecture**: Walk through agent workflow
6. **Future**: Discuss MCP integration potential

## 📝 Talking Points

- **"Secure by design"** - OAuth at every agent interaction
- **"Natural language first"** - No complex forms or UIs needed
- **"Enterprise ready"** - Full audit trail and compliance
- **"Extensible architecture"** - Easy to add new agent types
- **"MCP compatible"** - Ready for Model Context Protocol integration
