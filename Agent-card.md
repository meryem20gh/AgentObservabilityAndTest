# Agent Card: CI/CD Agents Security & Observability

## 1. Informations Générales
* **Nom du Système :** Security Guardrail & Knowledge Pipeline
* **Version actuelle :** v1.0.0
* **Type d'Architecture :** Graphe d'état orienté sécurité (LangGraph)
* **Contributeurs :** Meryem GHANEM, Fatima Ezzahra Elmenoun, Kola Ismail
* **Date de Création :** Juin 2026

## 2. Description de l'Architecture & Rôles
Le système est composé de trois agents orchestrés par un graphe d'état (`graph.py`) :
1.  **Guardrail Agent (`guardrail_agent`) :** Analyse l'entrée utilisateur pour détecter les attaques par injection de prompt (*Prompt Injection*). Si une anomalie est détectée, le statut passe à `INJECTION` et bloque l'exécution.
2.  **Knowledge Agent (`knowledge_agent`) :** Recherche une correspondance exacte ou sémantique dans la base de connaissances JSON (`knowledge.json`).
3.  **Fallback Agent (`fallback_agent`) :** S'active si aucune réponse n'est trouvée dans la base, renvoyant une réponse sécurisée par défaut sans interroger de LLM externe inutilement.

## 3. Spécifications Techniques & Dépendances
* **Runtime :** Python 3.10+
* **Orchestration :** LangGraph / Agentic Fusion AI
* **Observabilité :** Télémétrie en temps réel (Latence, Coût, Injection) via l'API Google Sheets & Dashboard Streamlit.
* **Sécurité :** Filtrage en amont (Guardrail) empêchant la fuite de données ou le détournement d'instructions.

## 4. Limites du Système & Biais Connus
* **Dépendance JSON :** Le `knowledge_agent` repose actuellement sur une correspondance exacte basée sur un fichier JSON statique. Les reformulations complexes peuvent déclencher le `fallback_agent`.
* **Faux Positifs :** Le `guardrail_agent` peut bloquer des requêtes légitimes contenant des mots-clés techniques s'apparentant à du code ou des instructions système.