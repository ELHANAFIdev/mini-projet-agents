# 📋 Runbook — Guichet Numérique Citoyen

## 1. Vue d'ensemble

Ce runbook décrit les procédures de gestion des incidents pour le Guichet Numérique Citoyen e-Gov Maroc.

**Contacts :**
- Équipe : ABA Technologie
- Escalade : Responsable formation Agentic AI

---

## 2. Incidents et procédures

### 🔴 INC-01 — Kill-Switch activé

**Symptôme** : `GET /health` retourne `{"kill_switch": true}`, toutes les requêtes `/invoke` retournent 503.

**Procédure :**
1. Vérifier la variable d'environnement : `echo $KILL_SWITCH_ENABLED`
2. Vérifier le fichier flag : `ls -la /tmp/egov_killswitch.flag`
3. **Pour réactiver** :
   - Env : `export KILL_SWITCH_ENABLED=false` puis redémarrer
   - Fichier : `rm /tmp/egov_killswitch.flag`
4. Vérifier : `curl http://localhost:8000/health`
5. Documenter la cause de l'activation dans le journal d'incidents

---

### 🟠 INC-02 — Circuit Breaker ouvert

**Symptôme** : `GET /health` retourne `{"circuit_breaker_open": true}`, requêtes `/invoke` retournent 503.

**Procédure :**
1. **Attendre le reset automatique** (60 secondes par défaut)
2. Vérifier les logs : `docker logs egov-maroc-agent --tail 50`
3. Chercher `circuit_breaker_failure` dans les logs
4. Identifier la cause racine :
   - Erreur API Groq → vérifier quota / clé API
   - Erreur réseau → vérifier connectivité
   - Erreur parsing → vérifier les prompts
5. Corriger la cause racine
6. Tester : `curl -X POST http://localhost:8000/invoke -H "Content-Type: application/json" -d '{"message": "test de santé"}'`

---

### 🟡 INC-03 — Latence élevée

**Symptôme** : Les réponses prennent > 5 secondes, le monitoring détecte des alertes latence.

**Procédure :**
1. Vérifier les `execution_logs` dans les réponses API
2. Identifier l'agent le plus lent
3. Actions possibles :
   - Réduire `max_tokens` dans l'agent concerné
   - Changer le modèle vers `llama-3.1-8b-instant` (plus rapide)
   - Vérifier le statut Groq : `https://status.groq.com`
4. Si persistant, activer le kill-switch et basculer sur un message de maintenance

---

### 🟡 INC-04 — Boucle Supervisor détectée

**Symptôme** : Logs montrent `supervisor_max_iterations`, réponse incomplète.

**Procédure :**
1. Vérifier les `execution_logs` — quel agent boucle ?
2. Causes fréquentes :
   - Agent ne set pas `next_agent = "FINISH"` → corriger le prompt
   - Supervisor ne parse pas la réponse JSON → vérifier le modèle
3. Le guard `MAX_ITERATIONS = 8` force l'arrêt automatique
4. Reproduire avec le même message pour diagnostiquer

---

### 🔴 INC-05 — Clé API Groq invalide

**Symptôme** : Toutes les requêtes `/invoke` retournent 500, logs montrent `AuthenticationError`.

**Procédure :**
1. Vérifier la clé : `echo $GROQ_API_KEY | head -c 10`
2. Tester la clé directement :
   ```bash
   curl https://api.groq.com/openai/v1/models \
     -H "Authorization: Bearer $GROQ_API_KEY"
   ```
3. Si invalide : générer une nouvelle clé sur `console.groq.com`
4. Mettre à jour : `.env` ou secret GitHub Actions
5. Redémarrer : `docker compose restart`

---

### 🟠 INC-06 — Erreur de classification Triage

**Symptôme** : Les demandes sont mal classifiées (mauvaise catégorie).

**Procédure :**
1. Collecter des exemples de mauvaise classification
2. Vérifier le prompt système dans `src/graph/nodes/triage.py`
3. Ajouter les cas problématiques comme exemples few-shot
4. Tester localement : `pytest tests/test_integration.py -v`
5. Déployer la correction

---

## 3. Commandes utiles

```bash
# Statut du service
curl http://localhost:8000/health | python -m json.tool

# Carte agent
curl http://localhost:8000/agent-card | python -m json.tool

# Test rapide
curl -X POST http://localhost:8000/invoke \
  -H "Content-Type: application/json" \
  -d '{"message": "Je veux un acte de naissance à Rabat"}'

# Logs Docker
docker logs egov-maroc-agent --tail 100 -f

# Redémarrage
docker compose restart

# Rebuild complet
docker compose down && docker compose up --build -d

# Activer kill-switch (urgence)
touch /tmp/egov_killswitch.flag

# Désactiver kill-switch
rm /tmp/egov_killswitch.flag
```

---

## 4. Checklist post-incident

- [ ] Cause racine identifiée
- [ ] Correction déployée
- [ ] Tests passés en CI
- [ ] Monitoring confirmé nominal
- [ ] Journal d'incident mis à jour
- [ ] Équipe notifiée
