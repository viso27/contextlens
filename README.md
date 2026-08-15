# 🔍 ContextLens — Dynamic AI Governance & Schema Drift Protection

> **A production-ready Model Context Protocol (MCP) proxy engine that prevents non-compliant SQL generation by enforcing real-time database governance rules on LLM outputs.**

---

## 🚀 Overview

As data warehouses evolve, database schemas undergo frequent changes—columns are deprecated, renamed, or hash-anonymized for privacy compliance (GDPR/CCPA). Standard LLMs generating SQL queries often rely on stale schema assumptions, leading to **query failures, financial mismatches, or security breaches**.

**ContextLens** solves this by establishing an active **governance boundary** between natural language prompts and SQL generation:

1. **Metadata Interception:** Real-time lookup of active vs. deprecated schema mappings across target database tables.
2. **Context Enrichment:** Dynamically injects MCP governance directives into the LLM system prompt prior to inference.
3. **Drift Benchmarking:** Runs targeted evaluation suites measuring **Schema Precision** and **Drift Recovery Rate**.

---

## ✨ Key Features

- 🛡️ **Dynamic MCP Governance Engine:** Intercepts deprecated column references (e.g., `gross_amount` → `net_revenue`, `user_phone` → `contact_phone_e164`) and forces compliant replacements.
- 🧪 **Interactive Query Sandbox:** Live side-by-side comparison of **Raw Un-governed LLM outputs** versus **ContextLens MCP-Enriched outputs**.
- 📊 **Targeted Eval & Benchmarking Suite:** Quantitative evaluation harness measuring query precision, drift recovery, and deprecation interception rates across enterprise domains.
- 🗄️ **Multi-Domain Schema Registry:** Pre-configured metadata schemas for **Fintech/Payments**, **SaaS Customer Billing**, and **Product Telemetry Logs**.
- 🌐 **Dynamic Schema Seeding API:** Endpoints and CLI tooling for dynamic database schema registration and live metadata updates.

---

## 🏗️ Architecture

```text
  [ User Prompt / Query ]
             │
             ▼
 ┌───────────────────────┐
 │   ContextLens Proxy   │ ◄── [ MongoDB Atlas Metadata Store ]
 └───────────┬───────────┘     (Active/Deprecated Column Rules)
             │
             ▼
 ┌───────────────────────┐
 │  MCP Context Injector │ ──► Appends Governance Rules & Replacement Notices
 └───────────┬───────────┘
             │
             ▼
  ┌─────────────────────┐
  │   LLM Inference     │ (Meta-Llama 3 / OpenRouter)
  └───────────┬─────────┘
             │
             ▼
  [ Governed, Compliant SQL Output ]
