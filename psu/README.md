# New Hampshire Digital Library Metadata Transforms

This repository contains some of the data analysis, modeling, and transformation (XSLT) work to be used by the New Hampshire Digital Library as part of an emerging DPLA hub.

It was built in Summer 2019.

## Files included

- [`analysis`](analysis) contains notes and reports used in writing the mappings and normalization rules
- [`scripts`](scripts) contains scripts used in analysis and normalization outputs
- [`xslt`](xslt) contains the XSLT for the Plymouth State University OAI Collections to be transformed to a proposed NHDL metadata application profile published primarily for DPLA harvesting.

## Proposed NHDL MAP Information

The proposed NHDL metadata application profile is documented [here](https://docs.google.com/spreadsheets/d/1mfe6_TjKcrgT2htG8P8OPvOqIfdvAreFVmQNgTMrKAg/edit#gid=948424764). This MAP focuses on
1. making the NHDL MAP flat for ease of analysis and transformation;
2. as close as possible to existing DPLA Hub [Qualified Dublin Core sources (in particular Ohio and District Digital)](https://docs.google.com/spreadsheets/d/1nUQmlW959p3j9sR-ic5cYL66mGUSIoIuSD550Ic1hk4/edit#gid=1503963979) for which crosswalks exist (so the DPLA tech team has an easier time ingesting this);
3. and mapping over fields that are only used by the targeted end DPLA MAP v.5 instead of trying to map over and normalize everything possible.

## XSLT Information

### Structure & Expansion Paths

The XSLT is written in 3 levels:
- collection-specific XSLT (`xslt/p15828coll*.xslt`): these are the files you actually run against the desired XML files. This imports the provider-specific XSLT (next).
- provider-specific XSLT (`xslt/psu.xslt`): this file is imported above and contains XML node templates that are reused across collections. If/when collections are consistent enough to use the same XSLT, this can be made into that. This imports the remediation XSLT (next).
- remediation-specific XSLT (`xslt/remediation.xslt`): this file has lookup parameters used by the above templates to normalize string values against a variety of vocabularies, including DCMI Types, the DPLA-recommended Getty AAT subset, Lexvo Language look-ups, targeted Geonames look-ups, month abbreviations, etc.

To run one of the collection-specific XSLT, you need to have all 3 files (collection specific XSLT, `psu.xslt`, and `remediation.xslt`) in the same directory.

### Reconciliation & Lookups

The remediation XSLT is generated to allow string to normalized string or URI lookups within the XSLT. You can expand it to have multiple string to desired value mappings; or change the XSLT templates using the lookups to match on whole strings (`matches()` or `. = $lookup/@string`), partial strings (`contains()`), or other aspects (`starts-with()`. `ends-with()`, etc.).

The longer vocabularies (e.g. Geonames) are targeted subsets, meaning we using the analysis scripts (or other means) to generate lists of the string in our source data that we wish to have reconciled (e.g. `dcterms:spatial`), then we run a script to match that against an external value and pull back what we wish to use in our lookup (the URI, external identifier, perhaps the normalized label, etc.). The output of this script is the XSLT param table we then put in `xslt/remediation.xslt`, and that is loaded and used with the XSLT templates that call it.

### Using XSLT in Combine

Combine has specific hangouts when using XSLT that imports other XSLT documents. See: https://combine.readthedocs.io/en/master/configuration.html?highlight=xslt#local-includes

Basically, to load these XSLT documents into Combine, the `psu.xslt` document requires a change at the top to either import a HTTP URL of the `remediation.xslt` file (like a raw document GitHub URL) or be changed *in Combine* to reference the auto-generated filepath for `remediation.xslt` within Combine. For the collection-specific XSLT documents, you need to change the import at the top of the document to either import a HTTP URL for `psu.xslt` or the Combine-generated filepath for `psu.xslt`.

If the above fails, a last ditch effort is to copy over `remediation.xslt` into `psu.xslt`, then copy over that aggregated `psu.xslt`into the collection-specific documents. This is less than ideal, as you lose the DRY (don't repeat yourself) structure of the XSLT.
