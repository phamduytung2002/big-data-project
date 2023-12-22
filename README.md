# Big data project - Vietnamese news clustering

## Prerequisite
- Window 10/11
- Docker desktop

## How to run
- Download data for producer from [here](https://www.kaggle.com/datasets/haitranquangofficial/vietnamese-online-news-dataset?rvi=1) and put it in news-producer/news_dataset.json

- Build containers and install libraries
  > build.bat

- Clear output of previous run (if exist)
  > hdfsclear.bat

- List files in folders
  > hdfsdls.bat

- Run kafka's producer and consumer
  > prod_cons.bat

- Batch process:
  > submit.bat  # convert output of consumer (.json files in hdfs) to csv file
  > submitmoel.bat  # run LDA on new batch
