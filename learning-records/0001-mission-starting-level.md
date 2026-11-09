# Mission and starting level established (session 1)

User's mission is to *ship* a fully autonomous crypto buy/sell agent in TypeScript, with decision logic adapted from prior research rather than invented; success = unattended agent + auditable decisions + paper-before-live discipline. Self-assessed TypeScript-basic; they selected nothing for trading or LLM-API experience, so assume both are new and teach vocabulary explicitly. "typesafe jev" was clarified as meaning "a research-grounded system to trigger buy/sell", not a specific library.

Implications: lessons should be architecture-first (agent loop), wire CCXT early for hands-on wins, cite research for every strategy claim, and defer ML training until the loop and cost model are understood.
