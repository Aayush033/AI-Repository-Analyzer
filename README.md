# 🔬 AI Repository Analyzer

> **An intelligent, multi-agent evaluation matrix designed to automate technical screening for recruiters and engineering managers.**

## 📌 Overview
The AI Repository Analyzer is a specialized tool built to bridge the gap between technical requirements and recruitment screening. By pasting a candidate's GitHub repository link, the system initiates a deep, multi-agent audit of the codebase, evaluating structural patterns, production readiness, and architectural integrity. 

It provides hiring teams with an immediate, readable 0-100 score and a detailed diagnostic matrix, drastically reducing the time spent on manual technical assessments.

## ✨ Key Features
* **Automated Code Auditing:** Scans repository structures for modern design patterns, testing pathways, and deployment configurations (Docker, CI/CD).
* **Live Sandbox Diagnostics:** Real-time environment compilation checks to ensure the candidate's code builds without syntax breakages.
* **Elite Architect Code Review:** AI-driven insights highlighting production risks, modularity, and overall engineering maturity.
* **Persistent Audit Ledger:** Automatically tracks and saves execution histories, allowing recruiters to pin, share, and compare candidate evaluations over time.
* **Sleek, Non-Blocking UI:** Built with Streamlit for a highly responsive, async-driven user experience.

## 🏗️ System Architecture & Security Notice
This repository serves as the **open-source frontend client** for the AI Repository Analyzer. 

To protect the proprietary intelligence and execution logic, the heavy-lifting multi-agent backend (powered by LLMs and asynchronous graph workflows) is isolated and securely maintained in a separate, private environment. 
* **Frontend:** Streamlit, Asyncio, UI/UX routing.
* **Backend (Private):** FastAPI, Multi-Agent Orchestration, Secure WebSockets.
