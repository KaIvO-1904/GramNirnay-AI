# GramNirnay.ai: Geospatial Rural Advisory & Micro-enterprise Intelligence

## Project Overview
GramNirnay.ai is an AI-driven hyper-local business advisory and financial structuring assistant designed specifically for rural micro-entrepreneurs. Unlike generic chatbots, GramNirnay.ai focuses on **Business Viability Before Financing**, helping entrepreneurs determine if a business idea is viable in their specific locality before recommending government schemes and financing options.

## Problem Statement (PS26091)
AI-Driven Hyper-Local Business Advisory and Financial Structuring Assistant for Rural Micro-Entrepreneurs.

## Core Philosophy
**Business Viability $\rightarrow$ Local Intelligence $\rightarrow$ Financial Modeling $\rightarrow$ Financing/Schemes.**

## Key Features
- **Hyper-Local Analysis**: Using geospatial and demographic data to assess market demand and competition.
- **Deterministic Financial Engine**: Accurate ROI, Break-even, and EMI calculations (non-LLM based).
- **RAG-Powered Scheme Matching**: Evidence-backed government scheme recommendations with source citations.
- **Explainable AI**: Every recommendation answers "Why?" with supporting data.
- **Risk-Aware Guidance**: Identification of local risks and suggestions for business modifications.

## Tech Stack (Proposed)
- **Frontend**: Next.js (App Router), Tailwind CSS, Lucide React, Recharts.
- **Backend**: FastAPI (Python) - ideal for AI/ML integration.
- **Database**: PostgreSQL + pgvector (for RAG).
- **LLM**: Claude 3.5 Sonnet (via API) for reasoning and synthesis.
- **Data**: Government open data, Kaggle, and synthetic local proxies for MVP.
