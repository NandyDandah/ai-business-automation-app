# Agensi tool setup

The skill uses tools through the user's connected Agensi MCP account. It does not need Hunter or Apollo API keys, and the FastAPI service does not call those providers directly. The agent performs searches/enrichment, then sends records to the app only when the user asks and a private authenticated API client is configured.

## Recommended tool cards

Agensi allows up to 10 tool cards on a skill. In the skill's Creator Studio editor, search for the current tools matching these jobs and add the exact cards. Names, availability, and prices can change, so check the live catalog rather than copying provider slugs or prices from this file.

1. Google Maps search for local businesses by keyword and location.
2. General web search for businesses, official websites, and source checks.
3. Apollo company search by industry, location, size, or technology.
4. Apollo people search by title, seniority, company, or location.
5. Apollo company enrichment by domain, company name, or LinkedIn URL.
6. Apollo person enrichment by email, LinkedIn URL, or name and company.
7. Hunter lookup for a company's domain from its name.
8. Hunter domain search for emails and roles at a company.
9. Hunter email finder for a named person and company domain.
10. Hunter email verification.

These cover local and B2B business discovery, decision-maker search, company context, professional email lookup, and validation. Use only the tools needed for a request. Apollo people search is a discovery step and may not return full contact details; use enrichment only for selected matches. Hunter domain results may have no verification status, so verify them when needed.

## Spend and privacy

- Search the current Agensi catalog and review its live price before setting cards.
- Before any paid tool run, quote the exact call count and total, tell the user what fields it should return, and wait for explicit approval. Agensi tool charges are separate from the skill's own price.
- Prefer official company websites for business-published facts. Label provider results as third-party enrichment and keep them separate in the app.
- Use business-relevant professional contact data only. Do not request or store private/home details, and do not send outreach.
- Agensi tool cards provide agent access; they do not add provider credentials to Render or this app.

## References

- [Agensi tools reference](https://www.agensi.io/docs/tools)
- [Agensi tool listing and limits](https://www.agensi.io/docs/what-you-can-sell)
- [Hunter tools](https://www.agensi.io/tools/hunter)
- [Apollo tools](https://www.agensi.io/tools/apollo)
- [Google Maps tools](https://www.agensi.io/tools/google-maps)

