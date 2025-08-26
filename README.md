# 📊 IIA Test Dashboard

A comprehensive Streamlit dashboard application with interactive data visualizations, deployable on Portainer.

## Features

- 📈 **Interactive Dashboard**: Real-time data visualization with Plotly
- 💰 **Revenue Analytics**: Comprehensive revenue analysis and reporting
- 👥 **Customer Insights**: Customer analytics and satisfaction metrics
- ⚙️ **Settings Panel**: Configurable application settings
- 🐳 **Docker Ready**: Fully containerized for easy deployment
- 🔄 **Auto-refresh**: Optional real-time data updates

## Quick Start

### Local Development

1. **Clone the repository**:
   ```bash
   git clone https://github.com/deepankar-MT24031/iia_test.git
   cd iia_test
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   streamlit run app.py
   ```

4. **Access the dashboard**:
   Open your browser and navigate to `http://localhost:8501`

### Docker Deployment

1. **Build and run with Docker Compose**:
   ```bash
   docker-compose up -d
   ```

2. **Access the application**:
   Open your browser and navigate to `http://localhost:8501`

## Portainer Deployment

### Method 1: Git Repository Integration (Recommended)

1. **In Portainer**:
   - Go to "Stacks" → "Add stack"
   - Choose "Git Repository"
   - Repository URL: `https://github.com/deepankar-MT24031/iia_test`
   - Compose path: `docker-compose.yml`
   - Click "Deploy the stack"

### Method 2: Upload Compose File

1. Copy the contents of `docker-compose.yml`
2. In Portainer: "Stacks" → "Add stack" → "Web editor"
3. Paste the compose file content
4. Click "Deploy the stack"

### Method 3: Portainer Agent/Edge

1. Set up Portainer Agent on your Docker host
2. Add the environment in Portainer
3. Deploy using Method 1 or 2

## Configuration

### Environment Variables

- `STREAMLIT_SERVER_PORT`: Port for the Streamlit server (default: 8501)
- `STREAMLIT_SERVER_ADDRESS`: Server address (default: 0.0.0.0)
- `STREAMLIT_SERVER_HEADLESS`: Run in headless mode (default: true)

### Streamlit Configuration

The application uses `.streamlit/config.toml` for Streamlit-specific settings:

- **Theme**: Custom color scheme
- **Server**: Port and address configuration
- **Browser**: Usage statistics and CORS settings
- **Client**: Caching and display options

## Project Structure

```
iia_test/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker container configuration
├── docker-compose.yml    # Multi-container deployment
├── .streamlit/
│   └── config.toml       # Streamlit configuration
├── .dockerignore         # Docker ignore rules
└── README.md            # This file
```

## Features Overview

### 📈 Dashboard Overview
- Key performance metrics
- Sales trend visualization
- Order distribution by category
- Real-time data updates

### 💰 Revenue Analysis
- Monthly revenue charts
- Revenue distribution analysis
- Category-wise revenue breakdown
- Statistical summaries

### 👥 Customer Analytics
- Regional customer distribution
- Customer satisfaction metrics
- Interactive scatter plots
- Customer data tables

### ⚙️ Settings & Configuration
- Auto-refresh settings
- Theme selection
- System health checks
- Application information

## Customization

### Adding New Charts

1. Create new data processing functions
2. Add Plotly chart configurations
3. Integrate with Streamlit layout
4. Update the sidebar filters

### Database Integration

Uncomment the PostgreSQL service in `docker-compose.yml` and:

1. Install database drivers: `pip install psycopg2-binary sqlalchemy`
2. Update `app.py` to connect to PostgreSQL
3. Replace sample data generation with database queries

### Redis Caching

Uncomment the Redis service for improved performance:

1. Install Redis client: `pip install redis`
2. Implement caching in `app.py`
3. Configure cache expiration times

## Health Monitoring

The application includes:

- **Docker Health Check**: Automatic container health monitoring
- **Streamlit Health Endpoint**: Built-in health check endpoint
- **Application Health Panel**: Manual health check functionality

## Troubleshooting

### Common Issues

1. **Port Already in Use**:
   ```bash
   # Change port in docker-compose.yml
   ports:
     - "8502:8501"  # Use different external port
   ```

2. **Memory Issues**:
   ```bash
   # Add memory limits to docker-compose.yml
   deploy:
     resources:
       limits:
         memory: 512M
   ```

3. **Permission Errors**:
   ```bash
   # Fix file permissions
   sudo chown -R $USER:$USER .
   ```

### Logs

View application logs:
```bash
# Docker Compose
docker-compose logs -f streamlit-app

# Direct Docker
docker logs iia-test-streamlit
```

## Development

### Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Test locally: `streamlit run app.py`
5. Test with Docker: `docker-compose up`
6. Submit a pull request

### Testing

```bash
# Install test dependencies
pip install pytest streamlit pytest-streamlit

# Run tests
pytest tests/
```

## Deployment Options

### Cloud Platforms

- **Heroku**: Deploy using `heroku.yml`
- **AWS ECS**: Use the Dockerfile for container deployment
- **Google Cloud Run**: Deploy containerized application
- **Azure Container Instances**: Single-container deployment

### Self-Hosted

- **Portainer**: Docker container management (recommended)
- **Docker Swarm**: Multi-node deployment
- **Kubernetes**: Enterprise-scale deployment

## License

This project is open source and available under the [MIT License](LICENSE).

## Support

For issues and questions:

1. Check the [GitHub Issues](https://github.com/deepankar-MT24031/iia_test/issues)
2. Create a new issue with detailed description
3. Include error logs and environment details

## Changelog

### v1.0.0
- Initial release
- Basic dashboard functionality
- Docker containerization
- Portainer deployment support
- Interactive data visualizations
- Configuration management
