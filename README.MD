# Ebay Kleinanzeigen API

<div align="center">
  <h3 align="center">Ebay Kleinanzeigen API</h3>

  <p align="center">
    A powerful API interface for Ebay-Kleinanzeigen.de that enables you to fetch listings and specific data.
  </p>

  <p align="center">
    <b>🚀 Looking for a ready-to-use solution?</b>
    <br />
    Try it at <a href="https://kleinanzeigen-agent.de/features/developer-api"><strong>kleinanzeigen-agent.de »</strong></a>
    <br />
    ✓ Automated Search Agents
    <br />
    ✓ Search & Detail API
    <br />
    <a href="https://github.com/DanielWTE/ebay-kleinanzeigen-api/issues">Report Bug</a>
    ·
    <a href="https://github.com/DanielWTE/ebay-kleinanzeigen-api/issues">Request Feature</a>
  </p>
</div>

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Getting Started

### Want to skip the setup?

Visit [kleinanzeigen-agent.de](https://kleinanzeigen-agent.de/features/developer-api) for our hosted solution with additional features and zero configuration required.

### Prerequisites

- Python 3.12 or higher
- pip (Python package manager)
- Playwright

### Installation

1. Clone the repository

```sh
git clone https://github.com/DanielWTE/ebay-kleinanzeigen-api.git
cd ebay-kleinanzeigen-api
```

2. Install dependencies

```sh
pip install -r requirements.txt
playwright install chromium
```

3. Start the API

```sh
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### Installation using UV

#### Prerequisites

- uv package manager

#### Installation of dependencies

```sh
uv sync
```

#### Start the API

```sh
uv run uvicorn main:app --reload
```

#### Optional Basic Auth

If you want to protect the API for tools like n8n, set both environment variables before starting the server.

The app also loads a local `.env` file automatically on startup, so the credentials can come either from shell environment variables or from `.env`. Existing process environment variables keep precedence over values from `.env`.

```sh
export BASIC_AUTH_USERNAME="n8n"
export BASIC_AUTH_PASSWORD="change-me"
uv run uvicorn main:app --reload
```

Example `.env`:

```dotenv
BASIC_AUTH_USERNAME=n8n
BASIC_AUTH_PASSWORD=change-me
```

If neither variable is set, authentication stays disabled. If only one is set, the API aborts on startup to avoid a half-configured setup.

### Installation using Docker

1. Build the Docker image

```sh
docker build -t ebay-kleinanzeigen-api .
```

2. Run the Docker container

```sh
docker run -p 8000:8000 ebay-kleinanzeigen-api
```

The API will be available at `http://localhost:8000`

### Docker Compose for n8n Network

There is also a ready-to-use Compose template in [docker-compose.yml](docker-compose.yml).

Typical usage:

```sh
cp .env.example .env
docker compose up -d --build
```

It expects that your n8n Docker network already exists and joins the API service to that external network. Adjust `N8N_DOCKER_NETWORK` in `.env` if your network has a different name.

Inside the shared Docker network, n8n can then reach the API via:

```text
http://kleinanzeigen-api:8000
```

If you add this service from a parent `docker-compose.yml`, the build context must point to the `kleinanzeigen` project directory, not the parent folder. Example:

```yaml
services:
  kleinanzeigen-api:
    build:
      context: ./kleinanzeigen
      dockerfile: Dockerfile
    container_name: kleinanzeigen-api
    env_file:
      - ./n8n_api_helper/.env
    ports:
      - "7999:8000"
    networks:
      - n8n
```

Why this matters:

- `COPY requirements.txt .` in the Dockerfile resolves relative to the Docker build context.
- If `context: .` points to the parent folder, Docker looks for `./requirements.txt` there instead of `./kleinanzeigen/requirements.txt`.
- The previous `playwright install-deps` step can also fail on newer Ubuntu package repositories; the current Dockerfile now uses the official Playwright Python base image, which already includes the matching browser runtime dependencies.

### API Endpoints

#### 1. Fetch Listings (Standard)

**Endpoint:** `GET /inserate`

**Description:** Retrieves a list of listings based on search criteria.

##### Query Parameters

- **`query`** *(string, optional)*: The search term (e.g., "fahrrad" to search for bicycles).
- **`location`** *(string, optional)*: The location or postal code to narrow the search (e.g., `10178` for Berlin).
- **`radius`** *(integer, optional)*: The search radius in kilometers from the specified location (e.g., `5` for a 5 km radius).
- **`min_price`** *(integer, optional)*: The minimum price in Euros for the listings (e.g., `200` for at least 200 Euros).
- **`max_price`** *(integer, optional)*: The maximum price in Euros for the listings (e.g., `500` for at most 500 Euros).
- **`page_count`** *(integer, optional)*: The number of pages to search or return (e.g., `5` for the first 5 pages, default is 1, max: 20 pages).
- **`exclude_adids`** *(string[], optional)*: Listing IDs that should be filtered out before the response is returned. Works with repeated parameters or comma-separated IDs.

##### Example Request

```http
GET /inserate?query=fahrrad&location=10178&radius=5&min_price=200&page_count=5
```

```http
GET /inserate?query=halbmarathon&location=10178&page_count=3&exclude_adids=1234567890,2345678901
```

#### 2. Fetch Listing Details

**Endpoint:** `GET /inserat/{id}`

**Description:** Retrieves detailed information about a specific listing.

##### Path Parameters

- **`id`** *(string)*: The unique identifier of the listing to fetch details for.

##### Example Request

```http
GET /inserat/12345
```

#### 3. Fetch Listings with Details (Combined)

**Endpoint:** `GET /inserate-detailed`

**Description:** Retrieves listings and their detailed information in a single request.

##### Query Parameters

Same as `/inserate` endpoint, plus:

- **`max_concurrent_details`** *(integer, optional)*: Maximum concurrent detail fetches (default: 5, max: 10).
- **`exclude_adids`** *(string[], optional)*: Listing IDs to skip before detail pages are fetched.

##### Example Request

```http
GET /inserate-detailed?query=laptop&page_count=2&max_concurrent_details=5
```

### Documentation

#### API Response Format

All API endpoints return responses in the following JSON format:

##### API Response Format

```json
{
  "success": true,
  "time_taken": 1.23,
  "unique_results": 100,
  "data": [...],
  "performance_metrics": {
    "pages_requested": 5,
    "pages_successful": 5,
    "success_rate": 100.0,
    "average_page_time": 2.45
  }
}
```

##### Combined Endpoint Response Format

```json
{
  "success": true,
  "time_taken": 3.45,
  "unique_results": 25,
  "data": [
    {
      "adid": "123456",
      "title": "Example Item",
      "price": "100",
      "details": {
        "id": "123456",
        "description": "Full description...",
        "seller": {...},
        "location": {...}
      }
    }
  ],
  "performance_metrics": {
    "listings_found": 25,
    "details_fetched": 25,
    "success_rate": 100.0
  }
}
```

## Performance Features

## 📊 Performance Benchmarks

Performance tests conducted on **Arch Linux** with **Intel i7-1260P** processor:

| Endpoint | Operation | Avg Time | Min Time | Max Time | Success Rate | Results |
|----------|-----------|----------|----------|----------|--------------|---------|
| Root | API status check | 0.004s | 0.001s | 0.009s | 100% | - |
| Listings | 1 page search | 1.209s | 1.081s | 1.596s | 100% | 25 |
| Listings | 5 pages search | 2.436s | 2.328s | 2.532s | 100% | 125 |
| Listings | 10 pages search | 4.989s | 4.790s | 5.229s | 100% | 250 |
| Details | Single listing details | 1.072s | 0.928s | 1.276s | 100% | 1 |
| Combined | 1 page + details | 9.058s | 8.804s | 9.319s | 100% | 25 |
| Combined | 2 pages + details | 17.512s | 17.063s | 18.038s | 100% | 50 |

### Performance Highlights

- **Single page search**: ~1.2s average response time
- **10-page search**: ~5.0s average response time  
- **Individual listing details**: ~1.1s average response time
- **Combined search + details**: ~9.1s average for 1 page with full details

*All tests performed with uvloop optimization and browser context pooling enabled.*

### 🚀 Technical Features

- **uvloop Integration**: High-performance asyncio event loop
- **Context Pooling**: Efficient browser resource reuse
- **Memory Optimization**: Automatic garbage collection and efficient processing
- **Intelligent Concurrency**: Optimal concurrent processing with resource control

### 🔧 Production Ready

- **Clean API Responses**: Minimal overhead with essential data only
- **Resource Management**: Automatic cleanup and efficient resource usage
- **Scalable Architecture**: Handles concurrent requests efficiently
- **Docker Optimized**: Fast container builds with uv package manager

API documentation is available at `http://localhost:8000/docs` when running locally.

### n8n Integration Notes

- Use the n8n `HTTP Request` node with authentication type `Basic Auth` if you enable the environment variables above.
- Persist already-notified `adid` values in n8n and send them back via `exclude_adids` on the next request.
- This keeps deduplication state outside the scraper process and avoids losing state after an API restart.
- A concrete n8n setup with `Data Table`, code snippets, and node order is documented in [docs/n8n-workflow.md](docs/n8n-workflow.md).

## License

Distributed under the MIT License. See `LICENSE` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>
