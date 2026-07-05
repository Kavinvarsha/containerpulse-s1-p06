import pandas as pd
import great_expectations as gx

df = pd.read_csv("metrics_ml_ready.csv", parse_dates=["timestamp"])

context = gx.get_context(mode="ephemeral")
data_source = context.data_sources.add_pandas("pandas_source")
data_asset = data_source.add_dataframe_asset(name="metrics_asset")
batch_definition = data_asset.add_batch_definition_whole_dataframe("batch")
batch = batch_definition.get_batch(batch_parameters={"dataframe": df})

# Define expectations
results = []
results.append(batch.validate(gx.expectations.ExpectColumnToExist(column="cpu")))
results.append(batch.validate(gx.expectations.ExpectColumnToExist(column="memory")))
results.append(batch.validate(gx.expectations.ExpectColumnValuesToNotBeNull(column="timestamp")))
results.append(batch.validate(gx.expectations.ExpectColumnValuesToBeBetween(column="cpu", min_value=0, max_value=1000000)))

print("📋 Validation Results:")
for r in results:
    status = "✅ PASS" if r.success else "❌ FAIL"
    print(f"  {status} — {r.expectation_config.type}")