# 📚 TAVILY API MINI-MANUAL (For LLM Injection)

> **Context:** Inject this block into Agent 2's prompt so it natively understands how to manipulate the Tavily Search API.

---

## TAVILY API: Search Configuration Rules

You have direct control over the Tavily Search API. When generating queries, you must configure the following parameters to ensure optimal data retrieval and zero token waste.

### 1. `search_depth` (String)
*   **"basic"**: Fast, lightweight search. Use this for general knowledge, news, or simple definitions.
*   **"advanced"**: Deep, comprehensive search. Tavily will read full webpage contents. **MUST USE** for coding syntax, technical specifications, or complex mechanisms.

### 2. `include_domains` (Array of Strings)
*   **Purpose:** A strict whitelist. Tavily will *only* search these websites.
*   **Rule:** If the topic requires absolute authority (Medicine, Law, Code), you MUST populate this list (e.g., `["react.dev", "nih.gov"]`). 
*   **Rule:** Leave empty `[]` if the topic is general and requires a broad web search.

### 3. `exclude_domains` (Array of Strings)
*   **Purpose:** A strict blacklist. Tavily will ignore these websites.
*   **Rule:** You MUST aggressively filter out SEO spam, unverified forums, and opinion sites for technical topics.
*   **Always Exclude:** `["reddit.com", "quora.com", "medium.com", "wikipedia.org"]` when fetching hard technical or scientific ground truth.

### 4. `include_raw_content` (Boolean)
*   **Purpose:** Tells Tavily to return the raw HTML/Markdown of the site.
*   **Rule:** Set to `true` ONLY if Agent 6 needs to extract a specific code snippet or math formula. Otherwise, set to `false` to save tokens.

### 5. `max_results` (Integer: 1 to 10)
*   **Rule:** Default to `3`. If the topic is highly obscure, increase to `5`. Never exceed `5` to prevent context window bloat for Agent 6.

---

## 🎯 FEW-SHOT EXAMPLES

**Scenario A: User wants to learn "React useEffect"**
```json
{
  "query": "React useEffect dependency array mechanics",
  "search_depth": "advanced",
  "include_domains": ["react.dev", "developer.mozilla.org"],
  "exclude_domains": ["reddit.com", "medium.com"],
  "include_raw_content": true,
  "max_results": 3
}
```

**Scenario B: User wants to learn "Latest SpaceX Launch"**
```json
{
  "query": "SpaceX latest Falcon 9 launch details",
  "search_depth": "basic",
  "include_domains": [],
  "exclude_domains": ["twitter.com", "x.com"],
  "include_raw_content": false,
  "max_results": 5
}
```
