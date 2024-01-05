# Big data project

## Prerequisite
- Window 10/11
- Docker desktop

## How to run
- Download data for producer from [here](https://www.kaggle.com/datasets/haitranquangofficial/vietnamese-online-news-dataset?rvi=1) and put it in news-producer/news_dataset.json

- Build containers and install libraries
  > docker-compose up -d

- Clear output of previous run (if exist)
  > hdfsclear.bat

- List files in folders
  > hdfsdls.bat

- Run kafka's producer and consumer
  > prod_cons.bat

- Set up cassandra (and insert dummy rows)
  > cass.bat

- Submit streaming job:
  > submit_streaming.bat

- Submit batch job:
  > submit.bat  # collect csv(s) from consumer
  > submitmoel.bat  # run LDA on new batch

- UI:
  > runUI.bat
