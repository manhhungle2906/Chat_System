# Distributed System Chat System - Full Functionalities Overview

This is a multi-user, multi-channel chat system built using Python and TCP sockets. It supports real-time messaging, private messages, file transfers, and various safety and scalability features.

---

## ✅ 1. Core Functionalities

| Feature                                | Description |
|----------------------------------------|-------------|
| **TCP-based Client-Server Chat**       | Clients connect to a central server via TCP sockets |
| **Multithreaded Server**               | Each client is handled in a separate thread to support concurrency |
| **Multiple Channels (Rooms)**          | Users can join, switch, and chat in named channels |
| **Active Channel Management**          | Messages are sent/received only within the active channel |
| **Private Messaging**                  | Use `/pm` to send direct messages to specific users |
| **Broadcast Messaging**                | Send messages to all users in the same active channel |
| **File Transfer over TCP**             | Send files (including images) using `/sendfile <nickname> <filepath>` |
| **Terminal-based Interface**           | Fully CLI-based for easy usage and testing |

---

## 🔧 2. User Commands Supported

| Command                   | Functionality |
|---------------------------|----------------|
| `/join <channel>`         | Join or create a new channel |
| `/switch <channel>`       | Switch active chat channel |
| `/list`                   | List users in the current channel |
| `/channels`               | List all active channels |
| `/whoami`                 | Show your nickname and joined channels |
| `/pm <nickname> <msg>`    | Send a private message |
| `/sendfile <nickname> <path>` | Send a file to a user |
| `/help`                   | Show list of available commands |
| `/quit`                   | Disconnect from server |

---

## 🛡️ 3. Safety & Restriction Features

| Feature                             | Description |
|-------------------------------------|-------------|
| **Rate Limiting**                  | Max 1 message per second per user |
| **Profanity Filter**               | Banned words (e.g. `fuck`, `shit`, `bitch`) are blocked |
| **Room Capacity Limit**            | Max 10 users per room |
| **Nickname Uniqueness Check**      | Prevent duplicate nicknames |
| **Message Validation**             | Prevent empty or malformed messages |
| **File Transfer Validation**       | Check if file exists and if target user is valid |
| **Command Validation**             | Unknown or incorrect commands are rejected |
| **Exception Handling**             | Prevent crashes and disconnects from breaking the system |

---

## 📡 4. Communication Behavior

| Scenario                            | Behavior |
|-------------------------------------|----------|
| Disconnects                        | Auto-cleanup, notify users in channels |
| Spam (fast messages)              | Rate limiting message shown |
| Banned word in message            | Message rejected with warning |
| Join full room                    | Access denied with message |
| File sent to user not found       | Server returns error |
| Message to inactive channel       | Not delivered |

---

## 🧱 5. System Design & Architecture

| Component              | Description |
|------------------------|-------------|
| **Threaded Server**   | One thread per client connection |
| **Socket-based Transfer** | Real-time messaging & file streaming |
| **Modular Command Handler** | All commands handled via a central function |
| **Dynamic Channel/User Mapping** | Dict-based storage for real-time room/user management |

---

## 🧊 Transparency

The system is transparent to the user.  
They interact with simple commands, without needing to understand the underlying TCP socket communication, threading, or message routing.

---

## 📈 Scalability

The server uses multithreading to support many clients at the same time.  
Channels and users are managed using dynamic data structures like dictionaries, which makes it easy to scale up without changing the code structure.

---
