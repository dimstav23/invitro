# InVitro

In-Vitro is a set of tools for analyzing the performance of serverless cluster deployments. In-Vitro consists of two tools, namely sampler and loader. Sampler creates representative workload summaries (i.e., samples of functions) based on production traces. Loader reconstructs the invocation traffic based on a given trace and steers this load to the functions deployed in the studied serverless cluster. Currently, In-Vitro supports [vHive](https://github.com/vhive-serverless/vHive) and [OpenWhisk](https://openwhisk.apache.org/). Documentation on how to use the sampler and the loader can be found in the `docs` folder.

Standard sampled traces are available in [data/traces/reference](data/traces/reference/) folder in this repository. The traces are sampled from the Azure Functions production traces using the [sampler](sampler) tool. More details on the sampling process can be found [here](docs/sampler.md#reference-traces).

## Reference our work

```
@inproceedings{ustiugov:invitro,
  author    = {Dmitrii Ustiugov and
               Dohyun Park and
               Lazar Cvetković and
               Mihajlo Djokic and
               Hongyu He and
               Boris Grot and
               Ana Klimovic},
  title     = {Enabling In-Vitro Serverless Systems Research},
  booktitle = {Proceedings of the 4th Workshop on Resource Disaggregation and Serverless (WORDS 2023)},
  publisher = {{ACM}},
  year      = {2023},
}
```

## Developing InVitro

### Getting help and contributing

We would be happy to answer any questions in GitHub Issues and encourage the open-source community
to submit new Issues, assist in addressing existing issues and limitations, and contribute their code with Pull Requests.
Please check our guide on [Contributing to vHive](https://github.com/vhive-serverless/vHive/blob/main/docs/contributing_to_vhive.md) if you would like contribute.
You can also talk to us in our [Slack space](https://join.slack.com/t/vhivetutorials/shared_invite/zt-1fk4v71gn-nV5oev5sc9F4fePg3_OZMQ).


## License and copyright

InVitro is free. We publish the code under the terms of the MIT License that allows distribution, modification, and commercial use.
This software, however, comes without any warranty or liability.

The software is maintained by the [EASL lab](https://systems.ethz.ch/research/easl.html) at ETH Zürich.

## Maintainers

* [Lazar Cvetkovic](https://github.com/cvetkovic) - lazar.cvetkovic@inf.ethz.ch

## Wallet notes
1. Get the [Azure function traces](https://github.com/Azure/AzurePublicDataset/blob/master/AzureFunctionsDataset2019.md) ([direct link](https://azurepublicdatasettraces.blob.core.windows.net/azurepublicdatasetv2/azurefunctions_dataset2019/azurefunctions-dataset2019.tar.xz)) and place them in `/data/azure`

2. Get all the requirements for the `sampler` as specified in [`/docs/sampler.md`](./docs/sampler.md)

3. Run the following to perform the sample from the Azure workloads:
```
python3 -m sampler preprocess  -t data/azure/ -o data/traces/azure_wallet/preprocessed_30 -s 06:08:00 -dur 30
python3 -m sampler sample -t data/traces/azure_wallet/preprocessed_30/ -orig data/traces/azure_wallet/preprocessed_30 -o data/traces/azure_wallet/sampled_500 -min 500 -st 10 -max 550 -tr 16
python3 -m sampler sample -t data/traces/azure_wallet/preprocessed_30/ -orig data/traces/azure_wallet/preprocessed_30 -o data/traces/azure_wallet/sampled_4000 -min 4000 -st 50 -max 4500 -tr 16
```


4. Generate the IATs for the chosen samples and generate the cumulative traces that are used for wallet::
```
mkdir -p wallet_traces/wallet_traces_500 wallet_traces/wallet_traces_4000

sed -i 's|"TracePath": "data/traces/example"|"TracePath": "data/traces/azure_wallet/sampled_500/samples/500"|' cmd/config_knative_trace.json
go run cmd/loader.go --config cmd/config_knative_trace.json --iatGeneration
python3 cumulative_trace_generator.py
rm iat*
mv function_invocations.csv wallet_traces/wallet_traces_500/

git checkout cmd/config_knative_trace.json

sed -i 's|"TracePath": "data/traces/example"|"TracePath": "data/traces/azure_wallet/sampled_4000/samples/4000"|' cmd/config_knative_trace.json
go run cmd/loader.go --config cmd/config_knative_trace.json --iatGeneration
python3 cumulative_trace_generator.py
rm iat*
mv function_invocations.csv wallet_traces/wallet_traces_4000/
``` 
Note that it uses the parameters set in [`cmd/config_knative_trace.json`](./cmd/config_knative_trace.json) to generate the IATs.
We do not execute the trace on actual serverless setup.

The configuration we use is the same as the one described in the [`Dirigent`](https://dl.acm.org/doi/10.1145/3694715.3695966) paper.
Specifically:
- 30-minute time window starting in the middle of the trace (8th hour of day 6)
- Medium sample: 500 functions with approx. 350k invocations
- Large sample: 4K functions with approx. 3.8M invocations