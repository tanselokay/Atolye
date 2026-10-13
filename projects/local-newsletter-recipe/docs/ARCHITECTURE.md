# DevWatch Architecture

DevWatch is an editorial operating system for technical knowledge.

It is not primarily a newsletter generator. The newsletter is one possible output of a broader editorial workflow whose purpose is to help a human editor discover, validate, understand, and communicate important technical developments.

## Mission

DevWatch helps a human editor turn noisy technical information into trustworthy editorial intelligence.

The system should produce useful daily signals first. Selected signals can then be expanded into deeper, peer-reviewed editorial packages and eventually newsletter-ready material.

## Design Philosophy

### Human editor first

DevWatch does not replace the editor. It gives the editor better candidates, better context, better questions, and better review artifacts.

The human editor remains the final authority for publication decisions.

### Reliability over intelligence

DevWatch does not optimize for using the single most intelligent model everywhere. It optimizes for editorial reliability.

A smaller, more specialized model that performs one role consistently can be more valuable than a larger general model that performs many roles inconsistently.

### Role-based agents

DevWatch prefers specialized roles over one general-purpose model.

Examples:

- Translator
- Signal Ranker
- Claim Extractor
- Technical Peer Reviewer
- Skeptical Reviewer
- Research Radar
- Editorial Rewriter
- Newsletter Writer

Each role can be benchmarked independently.

### Replaceable models

Roles are stable. Models are replaceable.

A model may serve multiple roles if it proves strong enough in benchmarks. Deployment should remain practical because local memory and storage are limited.

### Visible and overrideable decisions

Nothing important should happen silently.

Every recommendation should be explainable. Every model decision should be visible. The human editor can override any automated decision.

## Two Editorial Workflows

DevWatch has two related but distinct workflows.

### Daily Discovery Workflow

This workflow runs every day and produces a daily editorial intelligence brief.

```text
Sources / DEVONagent / RSS / Searches
        ↓
Discovery
        ↓
Signals
        ↓
Ranking and grouping
        ↓
Daily Brief
        ↓
Human selection
```

The daily brief should be useful even before the deeper architecture is complete. It should continue operating at the current implemented capability level while the system evolves.

The daily brief should include:

- candidate ideas and news signals
- important sources
- why each item may matter
- suggested follow-up topics
- early risk or quality notes where available

### Deep Editorial Workflow

This workflow starts when the human editor selects a topic, document, or signal for deeper work.

```text
Selected signal/topic
        ↓
Source collection
        ↓
Translation if needed
        ↓
Claim extraction
        ↓
Technical Peer Review
        ↓
Skeptical Review / Research Radar
        ↓
Editorial Rewrite
        ↓
Newsletter-ready brief
        ↓
Human approval
        ↓
Publication or archive
```

## Core Roles

### Signal Ranker

Ranks newly collected items and produces candidate editorial signals.

Output should explain why each signal matters, not only summarize it.

### Translator

Translates source material when needed. Translation is not editorial validation.

### Claim Extractor

Extracts concrete technical claims from a source document.

A claim should be reviewable, falsifiable where possible, and linked to source evidence.

### Technical Peer Reviewer

Acts as a technical referee before publication.

The reviewer challenges claims instead of merely summarizing them. It should identify:

- unsupported claims
- overgeneralizations
- hidden assumptions
- missing context
- counterexamples
- misleading definitions
- weak evidence

The reviewer should produce a verdict such as `accept`, `minor_revision`, `major_revision`, or `reject`, but this is advisory. The human editor decides.

### Skeptical Reviewer

A more aggressive reviewer role. Its purpose is to find what a normal reviewer may miss.

This role is especially useful for detecting:

- overly confident claims
- definition scope errors
- missing evidence
- internal inconsistencies
- hidden marketing framing

### Research Radar

Research Radar does not replace web search. It suggests what should be searched or verified.

Initial mode:

- produce search questions
- propose keywords
- identify likely counterexamples
- identify source types worth checking

Future mode:

- trigger DEVONagent template searches programmatically
- collect results through the same ingestion mechanism
- add high-quality sources and feeds to curated lists

### Editorial Rewriter

Uses peer review findings to turn a selected item into a safer editorial brief.

It should not hide uncertainty. It should incorporate reviewer cautions and safer wording.

### Newsletter Writer

Composes selected and approved editorial packages into a newsletter.

Newsletter writing is downstream from validation.

## DEVONagent Integration

DEVONagent is a major discovery and follow-up research component.

Future integration should support template searches such as:

- topic
- time range
- selected plugins
- preferred source domains
- result count
- crawl depth

Results should flow back into DevWatch as sources/signals rather than as unstructured notes.

As searches continue, DevWatch should accumulate:

- high-quality RSS feeds
- trusted source domains
- useful crawl targets
- low-quality or noisy sources to avoid

## Model Strategy

DevWatch uses a role-based model registry.

The system should support:

- primary model per role
- optional secondary/skeptical reviewer
- benchmark score per role
- manual override

A model can be reused across roles if it performs well enough and saves memory/storage.

The current working direction is to use at least two reviewers for deeper items:

- a balanced technical reviewer
- a skeptical reviewer

The exact model names are not architectural constants. They are deployment choices.

## Prompt Strategy

Prompts should be moved out of Python code and versioned as first-class project assets.

Planned structure:

```text
prompts/
    technical_peer_review.md
    technical_peer_review_glm.md
    technical_peer_review_gptoss.md
    research_radar.md
    editorial_rewrite.md
    newsletter_writer.md
```

Model-specific prompts are allowed when a model needs stricter language or JSON instructions.

## Guiding Product Principle

DevWatch's first production output is a daily editorial intelligence brief for the human editor.

The long-term output can include newsletters, technical briefs, research notes, and benchmark reports.

The product of DevWatch is not merely content. Its product is editorial confidence.
