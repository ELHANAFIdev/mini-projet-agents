# 🪪 Agent Card — Guichet Numérique Citoyen

## Identité

| Champ | Valeur |
|-------|--------|
| **Nom** | Guichet Numérique Citoyen |
| **Version** | 1.0.0 |
| **Type** | Multi-Agent Supervisor (LangGraph) |
| **Secteur** | e-Gov — Services Publics Maroc |
| **Auteur** | ABA Technologie |
| **Date création** | 2026-06-26 |
| **Statut** | Production-ready |

## Description

Architecture multi-agent orchestrée par un Supervisor LangGraph pour la digitalisation des services publics marocains. Le système classifie les demandes citoyennes et les route vers des agents spécialisés (documents administratifs, réclamations, guide procédures).

## Agents

| Agent | Modèle LLM | Rôle | Temperature |
|-------|------------|------|-------------|
| Supervisor | Groq llama-3.1-8b-instant | Orchestration et routing | 0 |
| Triage | Groq llama-3.1-8b-instant | Classification de demande | 0 |
| Document | Groq llama-3.1-8b-instant | Actes administratifs | 0.3 |
| Réclamation | Groq llama-3.1-8b-instant | Plaintes citoyennes | 0.3 |
| Guide | Groq llama-3.1-8b-instant | Orientation procédures | 0.4 |
| Monitoring | Aucun (rule-based) | Observabilité | N/A |

## Capacités

- Classification automatique des demandes citoyennes (4 catégories)
- Traitement des actes : naissance, casier judiciaire, résidence, certificat de vie
- Gestion des réclamations via portail chikaya.ma
- Orientation procédures avec portails marocains (watiqa.ma, idarati.ma, etc.)
- Observabilité : Correlation ID, métriques latence, alertes automatiques
- Kill-switch (env + fichier flag) et circuit breaker (3 erreurs consécutives)

## Limites et Risques

| Risque | Mitigation |
|--------|-----------|
| Hallucination LLM sur les procédures | Prompts contraints avec portails officiels |
| Boucle infinie supervisor | Guard MAX_ITERATIONS = 8 |
| Surcharge API Groq | Circuit breaker + rate limiting |
| Indisponibilité totale | Kill-switch + health check Docker |
| Données personnelles (CIN) | Pas de stockage — traitement stateless |

## Données

- **Entrée** : Message texte libre + CIN optionnel + ville optionnelle
- **Sortie** : Réponse structurée JSON avec catégorie, agent, logs
- **Stockage** : Aucun stockage persistant (stateless)
- **PII** : CIN transmis en mémoire uniquement, jamais persisté

## Déploiement

- **Runtime** : Python 3.11 / FastAPI / Uvicorn
- **Container** : Docker (image slim)
- **CI/CD** : GitHub Actions (lint → test → build)
- **Cloud** : Render / Railway / Fly.io
- **Health** : `GET /health` avec statut kill-switch et circuit-breaker

## Contact

- **Équipe** : ABA Technologie — Formation Agentic AI
- **Repo** : `github.com/<org>/egov-maroc-multi-agent`
