# Page Ordering Strategy - Report

This document explains my approach for page-order reconstruction and how I reached my best solution.

## Problem Setup

The task is to recover the original page order from shuffled pages.
At a basic level, this can be treated as a pairwise decision problem:

- Does page A come before page B?

I built and tested multiple methods around this idea.

## Method 1: Bi-Encoder + Cosine Similarity (Baseline)

My first working baseline was:

1. Take a **head snippet** (first few sentences/characters) from each page.
2. Take a **tail snippet** (last few sentences/characters) from each page.
3. Encode snippets using a pretrained sentence embedding model.
4. Compute cosine similarity between tail of page A and head of page B.
5. Use argmax-style next-page selection.

Why this made sense:

- It is simple and fast.
- It captures local continuation signal (end of one page to start of next page).
- It avoids full-page context limits by using focused head/tail snippets.

Main limitation:

- Greedy argmax can make early mistakes that propagate through the full sequence.

## Method 2: Cross-Encoder Scoring

Next, I tried a **Cross-Encoder** instead of only using independent embeddings.

Compared to Bi-Encoder:

- Bi-Encoder encodes pages separately and compares vectors.
- Cross-Encoder reads both inputs together and models token-level interaction.

Model family used:

- RoBERTa-based sentence/cross-encoder models (from `sentence-transformers` / `cross-encoder` checkpoints).

Why this is preferable for pairwise order:

- Better at local coherence decisions.
- Better at pronoun/reference continuity than plain cosine-only matching.

Still, local pair scoring alone was not enough to guarantee globally optimal page order.

## Method 3: Sequence Repair Heuristics

I also tested improvements over plain argmax:

- Build a k-length sequence window.
- Check if the chosen next page still matches sequence flow.
- If mismatch is detected, replace/reorder recent candidates.

This reduced some local errors, but it still depended on greedy behavior and did not solve global optimization well.

## Best Method: TSP-Based Global Ordering

My best score came from the **TSP-based approach** (implemented in `train1.py`).

Core idea:

1. Build pairwise transition scores between pages.
2. Convert those scores into an edge-cost matrix.
3. Solve for a global route that visits each page once with minimum total cost.

I used an asymmetric routing setup and OR-Tools style TSP path solving with a dummy-node trick for open-path behavior.

Why TSP worked best:

- It optimizes **global sequence quality**, not only local next-step confidence.
- It avoids many error cascades from greedy selection.
- It gave a clear and consistent score jump compared to earlier methods.

## Feature Engineering That Improved TSP

To make the transition signal stronger, I added these engineered features:

- Sentence splitting
- Head snippet extraction
- Tail snippet extraction
- Chapter flag / chapter number signal
- Length and structural cues

Then I used **PCA (Principal Component Analysis)** to keep important signals and reduce noisy dimensions before final modeling.

This helped stabilize learning and improved ranking quality.

## Other Methods I Tried

I also tried several additional ideas suggested by AI tools:

- Train a transformer directly on all 100-page text ordering
- Elo rating tournament style ranking
- Claude-style heuristic orchestration approach
- Give TSP output to an LLM for final verification/reranking

Observed result:

- These methods gave scores similar to, or lower than, the TSP pipeline.
- In practice, they added complexity without improving final ranking quality.

## Final Conclusion

The most reliable strategy for my setup was:

- Strong pairwise continuation signal (head/tail matching + semantic scoring)
- Good handcrafted structure features
- PCA for compact representation
- **TSP With Features as final global optimizer**

This combination gave the best performance among all methods I tested.
