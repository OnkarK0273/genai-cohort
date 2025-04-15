from openai import OpenAI
from dotenv import load_dotenv
import json
import os

load_dotenv()

api_key = os.getenv("api_key")
base_url = os.getenv("base_url")

client = OpenAI(
    api_key=api_key,
    base_url= base_url
)


# helper functions-------------------

# initial project setup create react app and express app

def initial_setup_from_input(input_data):
    # Frontend setup
    frontend = input_data.get("frontend")
    if frontend:
        print(f"🚀 Running frontend setup commands...")
        for cmd in frontend.get("commands", []):
            print(f"🔧 Executing: {cmd}")
            os.system(cmd)

    # Backend setup
    backend = input_data.get("backend")
    if backend:
        folder = backend.get("folder", "backend")
        print(f"🚀 Creating backend folder: {folder}")
        os.makedirs(folder, exist_ok=True)
        os.chdir(folder)

        for cmd in backend.get("commands", []):
            print(f"🔧 Executing: {cmd}")
            os.system(cmd)

        for subfolder in backend.get("folders", []):
            path = os.path.join(folder, subfolder) 
            os.makedirs(subfolder, exist_ok=True) # change from path to subfolder
            print(f"📁 Created backend subfolder: {path}")

        for file_name, content in backend.get("files", {}).items():
            path = os.path.join(folder, file_name)
            
            with open(file_name, 'w') as f: # changes from path to file_name
                f.write(content)
            print(f"📝 Created backend file: {path}")

        os.chdir("..")

# create folders

def create_folders(folders):
    for folder in folders:
        try:
            os.makedirs(folder, exist_ok=True)
            print(f"📁 Created folder: {folder}")
        except Exception as e:
            print(f"❌ Failed to create folder '{folder}': {e}")


# install packages
    
def install_packages(packages_dict):
    for section, packages in packages_dict.items():
        print(f"📦 Installing packages in '{section}': {', '.join(packages)}")
        os.chdir(section)
        os.system(f"npm install {' '.join(packages)}")
        print(f"✅ Installed packages in {section}: {', '.join(packages)}")
        os.chdir("..")


# write code files

def write_files(files):
    for path, content in files.items():
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w') as f:
                f.write(content)
            print(f"📝 Created file: {path}")
        except Exception as e:
            print(f"❌ Failed to write file '{path}': {e}")




available_tools = {
    "create_folders": {
        "fn": create_folders,
        "description": "Create folders based on list of folder paths"
    },
    "write_files": {
        "fn": write_files,
        "description": "Write files to specified paths with given content"
    },
    "install_packages": {
        "fn": install_packages,
        "description": "Install npm packages in frontend or backend"
    },
    "initial_setup_from_input": {
        "fn": initial_setup_from_input,
        "description": "Initial setup of frontend/backend from structured plan"
    },
}



system_propmt = """
You are helpfull coding assistant that can resolve user coding problems by using command line
you are work on following steps - start, plan, action, and observe mode
For the given user query and available tools, plan the step by step execution, based on the planning,
select the relevant tool from the available tool. and based on the tool selection you perform an action to call the tool.
Wait for the observation and based on the observation from the tool call resolve the user query.

Rules :
- follow the output JSON format
- always prefere one step at time and wait for next input
- carefully analyze the user query

available tools:
- create_folders : Create folders based on list of folder paths
- write_files : Write files to specified paths with given content
- install_packages : Install npm packages in frontend or backend
- initial_setup_from_input : Initial setup of frontend/backend from structured plan

output json format :
{{
"step" : string,
"content":"string"
"function":"name of the function if step is action"
"input" : "genrated input schema for the specific action"
}}

example :
user query - Create a full-stack project with authentication system
output : {{ "step": "start", "content": "User wants to create a full-stack project with authentication system" }}
output : {{ "step": "plan", "content": "First, I need to scaffold the project. I'll call initial_setup_from_input to generate frontend and backend boilerplate." }}
output : {{
  "step": "action",
  "function": "initial_setup_from_input",
  "input": {
    "frontend": {
      "commands": [ "npm create vite@latest frontend -- --template react", "npm install" ]
    },
    "backend": {
      "folder": "backend",
      "commands": [ "npm init -y", "npm install express" ],
      "folders": [ "routes", "controllers", "models" ],
      "files": {
        "index.js": "const express = require('express');\nconst app = express();\nconst PORT = process.env.PORT || 5000;\napp.use(express.json());\napp.listen(PORT, () => console.log(`Server running on port ${PORT}`));"
      }
    }
  },
  "content": "Running initial setup: scaffold frontend with Vite and backend with basic Express app structure"
}}
output : {{
  "step": "observe",
  "content": "Project scaffolding complete. Next, I'll install the necessary packages for full-stack authentication"
}}
output : {{
  "step": "action",
  "function": "install_packages",
  "input": {
    "frontend": ["axios"],
    "backend": ["bcrypt", "jsonwebtoken", "mongoose", "cors"]
  },
  "content": "Installing auth-related packages"
}}
output : {{
  "step": "observe",
  "content": "Packages installed. Now, I’ll create folders for auth-related backend and frontend files."
}}
output : {{
  "step": "action",
  "function": "create_folders",
  "input": [

    "frontend/src/pages/auth",
    "frontend/src/context"
  ],
  "content": "Creating folders to support authentication logic"
}}
output : {{
  "step": "observe",
  "content": "Folders created. Now I’ll write backend files for auth logic."
}}
output : {{
  "step": "action",
  "function": "write_files",
  "input": {
    "backend/models/User.js": "const mongoose = require('mongoose');\nconst userSchema = new mongoose.Schema({\n username: String,\n email: String,\n password: String\n});\nmodule.exports = mongoose.model('User', userSchema);"
    "backend/controllers/authController.js": "const jwt = require('jsonwebtoken');\nconst User = require('../models/User');\n...\nmodule.exports = { registerUser, loginUser };"
    
  },
  "content": "Writing backend auth files"
}}
output : {{
  "step": "observe",
  "content": "Backend files created. Now I’ll write frontend login/signup components and context."
}}
output : {{
  "step": "action",
  "function": "write_files",
  "input": {
    "frontend/src/pages/auth/Login.jsx": "import React, { useState } from 'react';\nimport { useNavigate } from 'react-router-dom';\n\nconst Login = () => {\n  const [email, setEmail] = useState('');\n  const [password, setPassword] = useState('');\n  const navigate = useNavigate();\n\n  const handleSubmit = (e) => {\n    e.preventDefault();\n    // Add login logic here (e.g., call API and set auth context)\n    console.log('Logging in with', email, password);\n    navigate('/dashboard');\n  };\n\n  return (\n    <div className=\"auth-form\">\n      <h2>Login</h2>\n      <form onSubmit={handleSubmit}>\n        <input type=\"email\" placeholder=\"Email\" value={email} onChange={(e) => setEmail(e.target.value)} required />\n        <input type=\"password\" placeholder=\"Password\" value={password} onChange={(e) => setPassword(e.target.value)} required />\n        <button type=\"submit\">Login</button>\n      </form>\n    </div>\n  );\n};\n\nexport default Login;",
    "frontend/src/pages/auth/Signup.jsx": "import React, { useState } from 'react';\nimport { useNavigate } from 'react-router-dom';\n\nconst Signup = () => {\n  const [email, setEmail] = useState('');\n  const [password, setPassword] = useState('');\n  const navigate = useNavigate();\n\n  const handleSubmit = (e) => {\n    e.preventDefault();\n    // Add signup logic here (e.g., call API to register user)\n    console.log('Signing up with', email, password);\n    navigate('/login');\n  };\n\n  return (\n    <div className=\"auth-form\">\n      <h2>Signup</h2>\n      <form onSubmit={handleSubmit}>\n        <input type=\"email\" placeholder=\"Email\" value={email} onChange={(e) => setEmail(e.target.value)} required />\n        <input type=\"password\" placeholder=\"Password\" value={password} onChange={(e) => setPassword(e.target.value)} required />\n        <button type=\"submit\">Signup</button>\n      </form>\n    </div>\n  );\n};\n\nexport default Signup;",
    "frontend/src/context/AuthContext.js": "import React, { createContext, useContext, useState } from 'react';\n\nconst AuthContext = createContext();\n\nexport const AuthProvider = ({ children }) => {\n  const [user, setUser] = useState(null);\n\n  const login = (userData) => setUser(userData);\n  const logout = () => setUser(null);\n\n  return (\n    <AuthContext.Provider value={{ user, login, logout }}>\n      {children}\n    </AuthContext.Provider>\n  );\n};\n\nexport const useAuth = () => useContext(AuthContext);"
  },
  "content": "Writing frontend auth files"
}}
output : {{
  "step": "observe",
  "content": "Frontend components added. Now I’ll integrate auth routes in core files."
}}
output : {{
  "step": "action",
  "function": "write_files",
  "input": {
    "backend/index.js": "const express = require('express');\nconst cors = require('cors');\nconst authRoutes = require('./routes/auth');\n\nconst app = express();\nconst PORT = process.env.PORT || 5000;\n\napp.use(cors());\napp.use(express.json());\n\napp.use('/api/auth', authRoutes);\n\napp.listen(PORT, () => {\n  console.log(`Server running on http://localhost:${PORT}`);\n});",
    "frontend/src/App.jsx": "import React from 'react';\nimport { BrowserRouter as Router, Routes, Route } from 'react-router-dom';\nimport Login from './pages/auth/Login';\nimport Signup from './pages/auth/Signup';\nimport { AuthProvider } from './context/AuthContext';\n\nconst App = () => {\n  return (\n    <AuthProvider>\n      <Router>\n        <Routes>\n          <Route path=\"/login\" element={<Login />} />\n          <Route path=\"/signup\" element={<Signup />} />\n        </Routes>\n      </Router>\n    </AuthProvider>\n  );\n};\n\nexport default App;"
  },
  "content": "Updating main files for route integration"
}}
output : {{ "step": "output", "content": "✅ Full-stack app with authentication system setup is complete" }}


"""

message = [{ "role": "system", "content": system_propmt }]

while True:
    
  query = input("Write your query > ")

  if query == 'close':
      break
  
  message.append({ "role": "user", "content": query })

  while True:

      res = client.chat.completions.create(
          model='gemini-2.0-flash',
          response_format={"type": "json_object"},
          messages=message
      )

      parsed_json = json.loads(res.choices[0].message.content)

      

      message.append({"role":"assistant", "content":json.dumps(parsed_json)})

      step = parsed_json.get("step")

      match step:
          case "start":
              print(f'🧠 start - {parsed_json.get("content")}')
              continue

          case "plan":
              print(f'🧠 plan - {parsed_json.get("content")}')
              continue

          case "action":
              tool_name = parsed_json.get("function")
              print(f'🛠️ action - Tool: {tool_name}')
              # print(f'🔧 Full payload: {parsed_json}')

              if available_tools.get(tool_name, False):
                  # Handle create_folders
                  if tool_name == "create_folders":
                      folders = parsed_json.get("input", [])
                      output = available_tools[tool_name]["fn"](folders)
                      message.append({ "role": "assistant", "content": json.dumps({ "step": "observe", "output": output }) })
                      continue

                  # Handle write_files
                  if tool_name == "write_files":
                      files = parsed_json.get("input", {})
                      output = available_tools[tool_name]["fn"](files)
                      message.append({ "role": "assistant", "content": json.dumps({ "step": "observe", "output": output }) })
                      continue

                  # Handle install_packages
                  if tool_name == "install_packages":
                      package_data = parsed_json.get("input", {})
                      output = available_tools[tool_name]["fn"](package_data)
                      message.append({ "role": "assistant", "content": json.dumps({ "step": "observe", "output": output }) })
                      continue

                  # Handle initial_setup_from_input
                  if tool_name == "initial_setup_from_input":
                      setup_data = parsed_json.get("input", {})
                      output = available_tools[tool_name]["fn"](setup_data)
                      message.append({ "role": "assistant", "content": json.dumps({ "step": "observe", "output": output }) })
                      continue

          case "output":
              print(f'✅ output - {parsed_json.get("content")}')
              break


    