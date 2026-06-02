AI Review System

An AI-powered review intelligence platform that collects, analyzes, and summarizes user opinions from multiple online sources.

⸻

Overview

AI Review System is a full-stack application designed to help users understand public opinions and sentiment around a specific topic.

Users can search for a topic, retrieve related comments, analyze sentiment, generate AI-powered summaries, and visualize the results through a modern dashboard.

The long-term goal is to evolve this project into a social listening and opinion intelligence platform capable of monitoring discussions across multiple platforms.

⸻

Features

Data Management

Store user comments in PostgreSQL
Organize comments by topic
Track platform and region information
Record creation timestamps
Analytics

Comment count statistics
Average sentiment calculation
Positive / Neutral / Negative distribution
Interactive charts and visualizations
AI Integration

AI-generated topic summaries
Large Language Model integration
Streaming summary output
Real-time analysis workflow
Dashboard

Modern Linear-inspired UI
Light / Dark mode
Responsive card layout
Smooth animations
Interactive data visualization
⸻

Tech Stack

Frontend

React
Vite
Axios
Recharts
Backend

FastAPI
SQLAlchemy
PostgreSQL
Pydantic
AI

NVIDIA API
OpenAI Compatible SDK
Development

Git
GitHub
⸻

Project Architecture

Frontend (React Dashboard)

↓

Backend API (FastAPI)

↓

Database (PostgreSQL)

↓

AI Analysis Layer

↓

Visualization Dashboard

⸻

API Endpoints

Comments

GET /comments

POST /comments

Statistics

GET /stats/{topic}

AI Summary

GET /summary/{topic}

⸻

Current Status

Completed:

FastAPI backend
PostgreSQL integration
SQLAlchemy ORM
Comment management
Topic statistics
Sentiment tracking
AI summary generation
Dashboard UI
Light/Dark mode
Streaming summary effect
Chart visualization
⸻

Future Roadmap

Phase 1

Fuzzy search
Enter-to-search support
Search history
Enhanced dashboard UX
Phase 2

Reddit integration
YouTube comment collection
Automated data ingestion
Phase 3

Topic extraction
AI-powered tagging
Trend analysis
Time-series sentiment tracking
Phase 4

Vector database integration
Semantic search
RAG-powered insights
AI Agent interface
Phase 5

User authentication
Multi-project management
SaaS deployment
Team collaboration
⸻

Motivation

Modern users generate massive amounts of feedback across social platforms every day.

This project explores how AI can transform raw comments into actionable insights through automated analysis, summarization, and visualization.

⸻

Author

Hou Linxing

AI Review System — Opinion Intelligence Platform
