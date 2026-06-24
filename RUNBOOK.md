# Runbook Opérationnel: Gestion des Incidents & Secours

Ce guide décrit les procédures d'urgence pour le projet **CI/CD Agents Security Observability**.

## 1. Gestion des Incidents Courants

### Incident A : Pic anormal de détection d'injections (Faux Positifs)
* **Symptôme :** Le taux d'injection sur le Dashboard Streamlit dépasse 30% et des utilisateurs légitimes sont bloqués.
* **Cause probable :** Une mise à jour récente du prompt du `guardrail_agent` est trop restrictive.
* **Action immédiate :** Analyser les logs sur Google Sheets pour identifier la signature des requêtes bloquées. Ajuster temporairement le prompt ou appliquer le **Kill-Switch**.

### Incident B : Rupture de la télémétrie (Dashboard vide)
* **Symptôme :** Streamlit n'affiche plus de nouvelles données.
* **Cause probable :** Expiration des identifiants `credentials.json` ou quota Google Sheets Apps Script atteint.
* **Action immédiate :** Vérifier la connectivité réseau dans `main.py` et s'assurer que l'URL `GOOGLE_SHEETS_WEBAPP_URL` répond à une requête POST manuelle (via Postman/cURL).

---

## 2. Procédure d'Urgence : Le Kill-Switch

Si le `guardrail_agent` devient fou (bloquant tout le trafic) ou si le pipeline consomme un budget LLM excessif, vous devez activer le mécanisme de secours pour contourner ou stopper le graphe.

### Option A : Kill-Switch Logiciel (Contournement du Guardrail)
Pour désactiver temporairement la vérification de sécurité sans couper l'application, modifiez la variable d'environnement dans votre fichier `.env` :
```env
DISABLE_GUARDRAIL=true