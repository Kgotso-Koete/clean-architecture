# 🗺️ Curriculum: Mastering DDD, TDD & Clean Architecture

This document tracks our roadmap for learning Domain-Driven Design, Test-Driven Development, and Clean Architecture using Python and Flask.

We will progress through each topic step by step, using the `clean-architecture` repo as our primary study material, and stealing modern patterns from the `python-ddd` repo as we advance.

### 🎯 Personal Context & Goals
- **Background**: Rethinking the entire work codebase. Moving from an intermediate software developer to mastering advanced architectural concepts.
- **The Problem**: Abstract concepts (repositories, ports, adapters) from books like *Cosmic Python* and *Obey the Testing Goat* are hard to grasp without practical application.
- **The Approach**: Learn by doing. We will mess around, modify this repository, add a UI, and break down each fundamental concept step-by-step using concrete code references.
- **The Ultimate Goal**: Understand this codebase inside out so it can serve as a rock-solid **template for future small business enterprise projects** (projects robust enough to scale, but maintainable by a single developer). 
- **Next Steps**: Once the foundation is solid, we will upgrade the template by incorporating the modern tooling and improvements outlined in `python-ddd/FUTURE_IMPROVEMENTS.md`.

### 📚 Course Materials
- **Primary Repo:** `clean-architecture` (Textbook Clean Architecture implementation)
- **Secondary Repo:** `python-ddd` (Modern tooling and DDD building blocks)
- **Book 1:** [Architecture Patterns with Python (Cosmic Python)](https://www.cosmicpython.com/book/preface)
- **Book 2:** [Test-Driven Development with Python](https://www.obeythetestinggoat.com/pages/book.html)

---

## The Learning Roadmap

| Chapter | Concept | Description | Status |
|:---:|---------|-------------|:---:|
| **1** | **The Big Picture & Core DDD** | What is Clean Architecture? The Dependency Rule. Understanding Entities vs Value Objects. | ✅ Done |
| **2** | **The Repository Pattern** | Introduction to Ports (Interfaces) & Adapters (Implementations). How to decouple the database from business logic. | ⏳ Next |
| **3** | **Use Cases (Application Services)** | The orchestrators of your system. How to map a user intent (Command/Query) to pure business logic. | 📝 Pending |
| **4** | **The Output Boundary & Presenter** | How to decouple the UI (Web, API, WhatsApp) from the application. Why Use Cases should never return HTTP responses. | 📝 Pending |
| **5** | **Domain Events & the Event Bus** | Decoupling side effects. How an Entity publishes an event, and how the Event Bus routes it to handlers. | 📝 Pending |
| **6** | **Dependency Injection** | Wiring it all together. How the framework (Flask/CLI) injects the right Adapters into the Use Cases. | 📝 Pending |
| **7** | **Process Managers (Sagas)** | Cross-module workflows. How to orchestrate complex, long-running processes (e.g., Auction Ends -> Payment -> Shipping). | 📝 Pending |
| **8** | **TDD in Practice** | Writing tests that don't break when you refactor. Testing Use Cases entirely in-memory without a real database. | 📝 Pending |
| **9** | **CQRS (Command Query Responsibility Segregation)** | Separating read models from write models for performance and simplicity. | 📝 Pending |
| **10** | **Bringing it all together** | Merging the best parts of `python-ddd` (modern tooling, strict base classes) into our Clean Architecture template. | 📝 Pending |
