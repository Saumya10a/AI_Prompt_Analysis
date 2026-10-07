# BDA Analytics Project: Faculty Presentation Guide

## Project in one minute

This project uses a synthetic JSON Lines (JSONL) dataset of 100,000 distinct prompt/response records across the same seven model labels to demonstrate an analytics pipeline. The backend loads and cleans records, derives metrics with Python/pandas, and independently aggregates them with local MapReduce-style code, PySpark DataFrames, and Spark SQL. A React dashboard presents the results. MongoDB can cache analytics when available, but it is optional: calculations use the local dataset.

Be precise about scale: this classroom implementation demonstrates Big Data Analysis concepts on 100,000 synthetic rows. Spark runs in local mode on this computer; it is not a distributed Spark cluster. The project does not run a distributed Hadoop cluster or use Sqoop for ingestion. Model outcome differences in this generated dataset are synthetic by design and are not real model benchmarks.

## Suggested demo flow

1. Start the backend and frontend with the repository's start scripts. Open the dashboard at the URL printed by the frontend.
2. On **Overview**, introduce the dataset and show the record, token, success, and quality summaries.
3. Open **Categories** to show aggregation by task domain; call out how workload distribution differs by category.
4. Open **Models** to compare record volume and outcomes across model labels, while noting this is descriptive rather than a controlled model benchmark.
5. Open **Reconciliation** to explain the independent calculation paths and inspect the deltas.
6. Open **Ecosystem** to show the real active path and optional infrastructure status honestly.
7. Finish in **Prompt Lab**. Run “Vague request”, then “Specific request”, and compare the rule-detected signals.

## Page-by-page talk track

### Overview — what is in the data?

**Click:** Overview (the home page).

**Say:** “This is the dataset-level summary. Each row is a prompt/response record. The API reads the JSONL file, preprocesses it, and aggregates these measures.”

**Explain the measures:** Total records is the number of valid records; total tokens is the sum of each record's `token_count`; average tokens per record is the total divided by valid records; unique categories and models are distinct labels; success rate is successful rows divided by all rows; quality score is the mean derived score.

**BDA connection:** This is descriptive analytics and summarization. It is the dashboard's overview of a data pipeline output, not a prediction model.

**Limit:** The quality score is a project-defined heuristic derived during preprocessing, not an externally validated quality measure.

### Categories — where is the workload?

**Click:** Categories.

**Say:** “Here the same records are grouped by task category. This answers which domains contribute most to volume and token use, and how the observed outcomes vary by domain.”

**Explain the measures:** Record count measures volume; token total and average show resource/workload demand; success rate and average quality summarize outcomes; models used lists model labels that appear in each group.

**BDA connection:** This demonstrates group-by aggregation, dimension-based analysis, and comparing cohorts. In a larger system, category could be a partitioning or reporting dimension.

**Click/show:** Compare the token and record charts, then read a row in the category detail table. Token count and record count answer different questions: one is usage, one is frequency.

### Models — how do the model groups compare?

**Click:** Models.

**Say:** “This groups records by model label instead of task category. We can compare usage and observed outcomes across these groups.”

**Explain the measures:** The page uses record count, token total/average, success rate, and average quality, plus categories processed.

**BDA connection:** This is multidimensional aggregation: the same dataset can be grouped by different attributes to explore different questions.

**Limit:** This is synthetic data with deliberately different per-model workloads and success probabilities to make aggregation differences visible. The charts explain group-by analysis and are not evidence that one real model is better.

### Reconciliation — do the calculations agree?

**Click:** Reconciliation; switch between All, Matched, and Mismatched if useful.

**Say:** “We compute comparable metrics through four paths: pandas, local MapReduce-style processing, the PySpark DataFrame API, and Spark SQL. Reconciliation checks that each implementation agrees on the same dataset.”

**Explain the measures:** Each row is one metric comparison. Absolute delta is the magnitude of the difference; percentage delta expresses the difference relative to the reference value when it can be calculated; match status applies the project's tolerance.

**BDA connection:** PySpark distributes dataframe operations across Spark partitions even though this demonstration uses one machine in local mode. Spark SQL expresses the same aggregates as SQL queries. Independent implementations and reconciliation help validate processing results.

**Limit:** The second implementation illustrates map, grouping/shuffle, and reduce in local Python. It is not Hadoop's distributed MapReduce runtime and does not prove cluster-scale performance.

### Ecosystem — what is actually required?

**Click:** Ecosystem.

**Say:** “This page shows the tools actually used: Python/pandas, local MapReduce-style aggregation, PySpark, and Spark SQL. Spark runs locally, so there is no external cluster. Hadoop, Sqoop, Hive, and Pig are optional and are not used in this implementation.”

**Explain the states:** Dataset indicates whether the input file exists. Python, local MapReduce-style code, PySpark, and Spark SQL make up the active processing paths. PySpark and Spark SQL execute in Spark local mode. MongoDB is an optional cache/persistence layer; when it is offline, analytics are still computed from the dataset, but results are not persisted. Hadoop, Sqoop, Hive, and Pig are readiness checks only.

**BDA connection:** A typical ecosystem separates ingestion, storage, processing, and presentation. This project models those concerns on a local scale so the concepts can be demonstrated without requiring cluster infrastructure.

**Be explicit:** The project reads the JSONL file directly; it does not use Sqoop to import from a relational database. Spark is applied through local-mode DataFrame and SQL analytics; this is not a distributed cluster deployment.

### Prompt Lab — what makes an instruction specific?

**Click:** Prompt Lab. Run **Try: Vague request**, inspect it, then run **Try: Specific request** and inspect again.

**Say:** “This is a rule-based text inspector, not a chatbot. It does not call an LLM or generate a response. It extracts measurable prompt features and gives deterministic suggestions.”

**Explain the output:** Word and character counts measure input size; code block count detects supported code formatting; detected constraints and format cues include supported length limits, exact item counts such as “exactly 5 points,” and formats such as “numbered list.” Specificity score is a heuristic based on length, action verbs, explicit wording, and detected constraints; hints are triggered by missing patterns such as context, an action, an example, or a length/format constraint.

**BDA connection:** The feature extraction illustrates turning unstructured text into simple structured signals that can be counted or summarized. The sample comparison helps explain how inputs can differ in specificity.

**Limit:** The score is not a scientific measure of prompt quality, factual correctness, or downstream model performance. The analyzer uses explicit regular-expression and keyword rules; patterns it does not recognize may not be detected.

## Data and processing explanation

- Input format: one JSON object per line in `data/sample_dataset.jsonl`; the generated demo dataset contains 100,000 distinct synthetic prompts and responses.
- Ingestion validates required text fields, normalizes text/timestamps, fills token count when missing, and derives a heuristic quality score.
- The Python baseline uses pandas grouping and aggregate operations.
- The local MapReduce-style path maps records to keys, groups values by key (the shuffle/grouping stage), then reduces each group into counts and totals.
- PySpark DataFrame and Spark SQL paths independently calculate overview, category, and model aggregates for the Reconciliation page using Spark local mode.
- The API serves overview, category, model, reconciliation, ecosystem, and prompt-inspection endpoints to the frontend.
- MongoDB stores cached analytics only when reachable. If unavailable, the backend should still serve calculations from JSONL; no database persistence is then available.

## Likely faculty questions

**Q: Why call this a Big Data Analysis project if it runs locally?**  
A: It demonstrates the analysis workflow and core patterns—ingestion, preprocessing, group-by metrics, map/group/reduce, and reconciliation—on a manageable sample. It is an educational prototype, not a claim that this machine processes production-scale data.

**Q: Where is Hadoop or Sqoop?**  
A: This project applies PySpark DataFrames and Spark SQL in local mode, and also demonstrates MapReduce-style aggregation locally. Hadoop and Sqoop remain optional: the demo reads JSONL directly and does not claim distributed Hadoop or Sqoop ingestion.

**Q: What happens if MongoDB is not running?**  
A: The dashboard's analytics are calculated from the local dataset. MongoDB-backed caching/persistence is skipped, so calculated results are not saved in the database.

**Q: Is the prompt score generated by AI?**  
A: No. It's deterministic rule-based parsing. The app detects supported keywords and patterns and calculates a heuristic score; it does not send the prompt to a model.

**Q: Does a higher model success rate mean that model is better?**  
A: Not necessarily. This is a descriptive comparison of the records available. Task mix, sample sizes, and data generation can affect the rates, so a controlled experiment would be needed to claim comparative model performance.

**Q: What would be the next scale-up step?**  
A: Move the Spark jobs to a multi-node cluster and add distributed storage such as HDFS; the same aggregates and reconciliation checks could then run over partitioned data at larger scale. That cluster deployment is a proposed extension, not part of this local demo.
