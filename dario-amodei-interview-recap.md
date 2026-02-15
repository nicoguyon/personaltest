# Recap : Dario Amodei - "We are near the end of the exponential"

**Interview** : Dwarkesh Podcast (Dwarkesh Patel), publiee le 13 fevrier 2026
**Duree** : ~2h22
**Source** : [dwarkesh.com/p/dario-amodei-2](https://www.dwarkesh.com/p/dario-amodei-2)

---

## La phrase choc : "Nous sommes proches de la fin de l'exponentielle"

Dario ne dit PAS que l'IA stagne. Il dit le contraire : on approche de la **ligne d'arrivee**. Le mot "fin" fait reference a l'aboutissement, pas au ralentissement. Les systemes IA vont bientot etre meilleurs que n'importe quel humain sur n'importe quelle tache cognitive. C'est ce qu'il appelle "a country of geniuses in a data center" - un pays de genies dans un data center.

Ce qui le surprend le plus ? **Le manque de prise de conscience du grand public**. Il trouve "absolument dingue" que les gens restent focalises sur les memes sujets politiques alors qu'on est a ce point d'inflexion.

---

## Les points cles

### 1. Timelines AGI : c'est pour demain (ou presque)

- **50/50** : "country of geniuses" dans **1 a 2 ans** (2027-2028)
- **90% de confiance** : avant **2035**
- **95% de confiance** : automatisation complete du software engineering dans **1-2 ans**
- Incertitude residuelle de ~5% liee aux risques geopolitiques (invasion de Taiwan, destruction de fabs)
- Il reconnait pouvoir se tromper d'un an ou deux, mais pas plus

### 2. Revenus d'Anthropic : une croissance x10 chaque annee

- **2023** : ~100M$ de revenus annuels
- **2024** : ~1 milliard $
- **2025** : ~9-10 milliards $
- **Janvier 2026 seul** : "encore quelques milliards" supplementaires
- Objectif a horizon pre-2030 : des trillions de revenus annuels
- La courbe ne montre aucun signe de ralentissement

### 3. L'hypothese du "Big Blob of Compute" tient toujours

Son hypothese de 2017 repose sur 7 facteurs : compute brut, quantite de donnees, qualite/distribution des donnees, duree d'entrainement, fonctions objectif scalables, et stabilite numerique. Cette grille de lecture fonctionne aussi bien pour le pre-training que pour le RL (Reinforcement Learning).

**Point important** : le RL suit exactement les memes lois de scaling que le pre-training. Ce ne sont pas deux paradigmes differents - c'est le meme phenomene.

### 4. Le software engineering transforme en premier

- **90% du code est deja ecrit par l'IA** dans certaines entreprises
- MAIS 90% du code ecrit =/= 90% des developpeurs remplaces (un compilateur ecrit 100% du code machine)
- Le spectre de progression : 90% du code par IA → 100% du code → 90% des taches end-to-end → 100% des taches
- Des collegues chez Anthropic n'ecrivent deja plus aucune ligne de code manuellement
- La generation de GPU kernels se fait deja sans intervention humaine
- **Claude Code** : cree initialement comme outil interne ("Claude CLI"), adopte massivement en interne avant le lancement public

### 5. Le piege de l'investissement compute

C'est le passage le plus frappant sur les risques business :

> "S'il y a un ecart meme leger - disons 800 milliards au lieu de 1 trillion de revenus - il n'y a aucune force sur terre, aucune couverture sur terre qui pourrait m'empecher de faire faillite."

- La croissance compute de l'industrie : 3x par an (10-15 GW → 30-40 GW → 100 GW → 300 GW en 2029)
- Chaque gigawatt = 10-15 milliards $/an
- Se tromper d'un an sur les previsions de croissance = faillite potentielle
- C'est pourquoi Anthropic est prudent sur le compute malgre ses convictions sur les timelines

### 6. Profitabilite : le modele est rentable, pas (encore) l'entreprise

- L'inference a des marges brutes >50%
- Le training represente ~50% des depenses compute
- Chaque modele individuellement est rentable
- Les pertes viennent du reinvestissement dans le modele suivant et des erreurs de prediction de demande (achat de data centers 1-2 ans a l'avance)
- L'equilibre arrive quand la prediction de la demande devient fiable - autour de la phase "country of geniuses"

### 7. Diffusion economique : rapide mais pas instantanee

- L'adoption en entreprise necessite : revue juridique, securite, conduite du changement
- La diffusion est BEAUCOUP plus rapide que pour les technologies historiques
- Mais pas instantanee : des mois de processus pour chaque entreprise
- Dario anticipe une **croissance economique de 10-20% par an** (vs. 300%+ de croissance compute)
- Le vrai risque : les benefices se concentrent dans la Silicon Valley (~50% de croissance) tandis que le reste stagne (5-10%)

### 8. Verification vs. generalisation

- Les taches **verifiables** (code, maths) progressent plus vite
- MAIS il y a deja une **generalisation significative** entre domaines
- Un modele entraine sur le code generalise au planning et aux taches creatives
- Incertitude restante sur les taches **non-verifiables** : ecriture de roman, decouverte scientifique fondamentale, planification d'une mission Mars
- Dario : "Je suis presque certain qu'on a un chemin fiable pour y arriver, mais s'il y a un peu d'incertitude, c'est la"

### 9. Robotique : 1-2 ans apres le software

- Pas besoin d'apprentissage continu type humain
- Les modeles entraines sur des simulations/jeux/videos generalisent au controle physique
- Quand les modeles maitrisent le software engineering → la robotique suit rapidement
- Impact sur le monde physique : 1-2 ans supplementaires apres l'automatisation software

### 10. Structure de l'industrie : un oligopole type cloud

- L'IA va ressembler au cloud computing : **3-4 acteurs majeurs**
- Les barrieres a l'entree sont enormes (capital + expertise)
- Contrairement au cloud, les modeles montrent une **vraie differentiation** (coding vs. raisonnement, style)
- Les nouveaux entrants reduisent les marges mais ne les eliminent pas
- Les APIs restent viables a long terme car les progres creent constamment de nouveaux cas d'usage

---

## Les citations marquantes pour un post LinkedIn

- "We are near the end of the exponential" - on est proche de la fin de l'exponentielle
- "A country of geniuses in a data center" - un pays de genies dans un data center
- "The lack of public recognition of how close we are... is absolutely wild" - le manque de prise de conscience est absolument dingue
- "There's no force on earth, no hedge on earth that could stop me from going bankrupt" (si les previsions sont decalees)
- "90% of code written by AI" - 90% du code deja ecrit par l'IA
- "I think it's crazy to say that this won't happen by 2035" - c'est fou de dire que ca n'arrivera pas d'ici 2035
- "Extremely fast but not instant" - extremement rapide mais pas instantane

---

## Angles possibles pour un post LinkedIn

1. **Le paradoxe de la fin de l'exponentielle** : Dario dit que ca se termine, mais en fait c'est l'inverse - on arrive au but. Decalage entre perception publique et realite technique.

2. **Le piege a 1 trillion $** : Comment se tromper d'un an sur une prevision peut mener a la faillite. Le plus gros pari economique de l'histoire.

3. **90% du code par IA =/= 90% des devs remplaces** : Pourquoi cette distinction est cruciale et ce que ca veut dire pour les equipes tech.

4. **La concentration geographique des benefices de l'IA** : Le vrai risque societal selon Dario - Silicon Valley a +50% vs. le reste du monde a +5%.

5. **La course a l'AGI en chiffres** : De 100M$ a 10 milliards en 2 ans, avec l'objectif des trillions avant 2030.
