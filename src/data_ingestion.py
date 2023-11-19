import argparse
import datetime

from logger import get_logger
from utils import (
    perform_get_request,
    xml_to_gen_data,
    xml_to_load_dataframe,
)

logger = get_logger()


def process_load_chunk(regions, start, end, output_path) -> None:
    # URL of the RESTful API
    url = "https://web-api.tp.entsoe.eu/api"

    # General parameters for the API
    # Refer to https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.html#_documenttype
    params = {
        # "securityToken": "1d9cd4bd-f8aa-476c-8cc1-3442dc91506d",
        "securityToken": "fb81432a-3853-4c30-a105-117c86a433ca",
        "documentType": "A65",
        "processType": "A16",
        "outBiddingZone_Domain": "FILL_IN",  # used for Load data
        "periodStart": start,
        "periodEnd": end,
    }

    # Loop through the regions and get data for each region
    for region, area_code in regions.items():
        logger.info(f"Fetching data for {region}...")
        params["outBiddingZone_Domain"] = area_code

        # Use the requests library to get data from the API for the specified time range
        response_content = perform_get_request(url, params)

        # Response content is a string of XML data
        df = xml_to_load_dataframe(response_content)

        # Save the DataFrame to a CSV file
        df.to_csv(f"{output_path}/load_{region}.csv", index=False)


def get_load_data_from_entsoe(regions, periodStart="202201010000", periodEnd="202301010000", output_path="./data"):
    # Raise exception if periodStart is after periodEnd
    if periodStart > periodEnd:
        raise ValueError("periodStart must be before periodEnd")

    # If range is grater than 1 year, process in 1 year chunks
    if datetime.datetime.strptime(periodEnd, "%Y%m%d%H%M") - datetime.datetime.strptime(
        periodStart, "%Y%m%d%H%M"
    ) > datetime.timedelta(days=365):
        logger.info("Period range is more than 1 year. Processing in 1 year chunks...")

        # Define the initial and final dates for the chunks
        start_date = datetime.datetime.strptime(periodStart, "%Y%m%d%H%M")
        end_date = datetime.datetime.strptime(periodEnd, "%Y%m%d%H%M")
        one_year = datetime.timedelta(days=365)

        while start_date < end_date:
            # Adjust the chunk end date to avoid exceeding the provided end_date
            chunk_end_date = min(start_date + one_year, end_date)

            # Get the start and end strings for the API call
            start_str = start_date.strftime("%Y%m%d%H%M")
            end_str = chunk_end_date.strftime("%Y%m%d%H%M")

            # Process data for the chunk
            process_load_chunk(regions, start_str, end_str, output_path)

            # Move to the next chunk
            start_date += one_year

    else:
        # Get the start and end strings for the API call
        start_str = periodStart
        end_str = periodEnd

        # Process data for the chunk
        process_load_chunk(regions, start_str, end_str, output_path)

        return


def process_gen_chunk(regions, start, end, output_path) -> None:
    # URL of the RESTful API
    url = "https://web-api.tp.entsoe.eu/api"

    # General parameters for the API
    params = {
        "securityToken": "1d9cd4bd-f8aa-476c-8cc1-3442dc91506d",
        "documentType": "A75",
        "processType": "A16",
        "outBiddingZone_Domain": "FILL_IN",  # used for Load data
        "in_Domain": "FILL_IN",  # used for Generation data
        "periodStart": start,
        "periodEnd": end,
    }

    # Loop through the regions and get data for each region
    for region, area_code in regions.items():
        logger.info(f"Fetching data for {region}...")
        params["outBiddingZone_Domain"] = area_code
        params["in_Domain"] = area_code

        # Use the requests library to get data from the API for the specified time range
        response_content = perform_get_request(url, params)

        # Response content is a string of XML data
        dfs = xml_to_gen_data(response_content)

        # Save the dfs to CSV files
        for psr_type, df in dfs.items():
            # Save the DataFrame to a CSV file
            df.to_csv(f"{output_path}/gen_{region}_{psr_type}.csv", index=False)


def get_gen_data_from_entsoe(
    regions, periodStart="202302240000", periodEnd="202303240000", output_path="./data"
) -> None:
    # Raise exception if periodStart is after periodEnd
    if periodStart > periodEnd:
        raise ValueError("periodStart must be before periodEnd")

    # If range is grater than 1 year, process in 1 year chunks
    if datetime.datetime.strptime(periodEnd, "%Y%m%d%H%M") - datetime.datetime.strptime(
        periodStart, "%Y%m%d%H%M"
    ) > datetime.timedelta(days=365):
        logger.info("Period range is more than 1 year. Processing in 1 year chunks...")

        # Define the initial and final dates for the chunks
        start_date = datetime.datetime.strptime(periodStart, "%Y%m%d%H%M")
        end_date = datetime.datetime.strptime(periodEnd, "%Y%m%d%H%M")
        one_year = datetime.timedelta(days=365)

        while start_date < end_date:
            logger.info(f"Fetching data for range {start_date} to {start_date + one_year}")

            # Adjust the chunk end date to avoid exceeding the provided end_date
            chunk_end_date = min(start_date + one_year, end_date)

            # Get the start and end strings for the API call
            start_str = start_date.strftime("%Y%m%d%H%M")
            end_str = chunk_end_date.strftime("%Y%m%d%H%M")

            # Process data for the chunk
            process_gen_chunk(regions, start_str, end_str, output_path)

            # Move to the next chunk
            start_date += one_year
    else:
        # Get the start and end strings for the API call
        start_str = periodStart
        end_str = periodEnd

        # Process data for the chunk
        process_gen_chunk(regions, start_str, end_str, output_path)

    return


def parse_arguments():
    parser = argparse.ArgumentParser(description="Data ingestion script for Energy Forecasting Hackathon")
    parser.add_argument(
        "--start_time",
        type=lambda s: datetime.datetime.strptime(s, "%Y-%m-%d"),
        default=datetime.datetime(2023, 1, 1),
        help="Start time for the data to download, format: YYYY-MM-DD",
    )
    parser.add_argument(
        "--end_time",
        type=lambda s: datetime.datetime.strptime(s, "%Y-%m-%d"),
        default=datetime.datetime(2023, 1, 2),
        help="End time for the data to download, format: YYYY-MM-DD",
    )
    parser.add_argument("--output_path", type=str, default="./data", help="Name of the output file")
    return parser.parse_args()


def main(start_time, end_time, output_path):
    regions = {
        "HU": "10YHU-MAVIR----U",
        "IT": "10YIT-GRTN-----B",
        "PO": "10YPL-AREA-----S",
        "SP": "10YES-REE------0",
        "UK": "10Y1001A1001A92E",
        "DE": "10Y1001A1001A83F",
        "DK": "10Y1001A1001A65H",
        "SE": "10YSE-1--------K",
        "NE": "10YNL----------L",
    }

    # Transform start_time and end_time to the format required by the API: YYYYMMDDHHMM
    start_time = start_time.strftime("%Y%m%d%H%M")
    end_time = end_time.strftime("%Y%m%d%H%M")

    # Get Load data from ENTSO-E
    get_load_data_from_entsoe(regions, start_time, end_time, output_path)

    # Get Generation data from ENTSO-E
    get_gen_data_from_entsoe(regions, start_time, end_time, output_path)


if __name__ == "__main__":
    logger.info("-" * 50)
    logger.info("Starting data ingestion...")
    # args = parse_arguments()
    # main(args.start_time, args.end_time, args.output_path)

    # Test
    logger.info("Testing - Fetching data from ENTSO-E...")
    main(datetime.datetime(2022, 1, 1), datetime.datetime(2023, 1, 1), "../data")
