# GPUStack UI Monitoring with Grafana and Prometheus

This guide explains how to benefit from Grafana and Prometheus monitoring for your GPUStack UI deployment.

## 🎯 Benefits of Monitoring

### 1. **Real-time System Health**
- **Service Availability**: Monitor if your backend is running and responding
- **Performance Metrics**: Track CPU, memory, and request rates
- **Database Health**: Ensure database connectivity and performance
- **Error Detection**: Identify issues before they affect users

### 2. **Performance Optimization**
- **Request Patterns**: Understand usage patterns and peak times
- **Resource Utilization**: Monitor CPU and memory usage
- **Concurrent Users**: Track active connections and user load
- **Response Times**: Identify slow endpoints and bottlenecks

### 3. **Capacity Planning**
- **User Capacity**: Understand how many users your system can handle
- **Scaling Decisions**: Know when to scale up resources
- **Resource Forecasting**: Plan for future growth

### 4. **Operational Insights**
- **Uptime Monitoring**: Track service availability
- **Error Tracking**: Monitor and alert on failures
- **Trend Analysis**: Understand long-term performance patterns

## 🚀 Quick Start

### 1. Start Monitoring Services

```bash
# Start the monitoring stack
docker-compose -f docker-compose.mac-prod.yml up -d prometheus grafana

# Check if services are running
docker-compose -f docker-compose.mac-prod.yml ps
```

### 2. Access Monitoring Dashboards

- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090

### 3. View Your Dashboard

The GPUStack UI dashboard will be automatically loaded in Grafana with:
- System health overview
- CPU and memory usage
- Active connections
- Request rates
- Database health
- Service uptime

## 📊 Key Metrics Explained

### System Health Metrics
- **`gpustack_ui_up`**: Service availability (1 = healthy, 0 = down)
- **`gpustack_ui_uptime_seconds`**: How long the service has been running
- **`gpustack_ui_database_status`**: Database connectivity (1 = healthy, 0 = error)

### Performance Metrics
- **`gpustack_ui_active_connections`**: Current HTTP connections
- **`gpustack_ui_total_requests`**: Total requests since startup
- **`gpustack_ui_requests_per_minute`**: Request rate
- **`gpustack_ui_avg_concurrent_users`**: Average concurrent users

### Resource Metrics
- **`gpustack_ui_system_cpu_percent`**: CPU usage percentage
- **`gpustack_ui_system_memory_percent`**: Memory usage percentage
- **`gpustack_ui_system_memory_available_mb`**: Available memory in MB

## 🔍 Advanced Monitoring

### 1. Custom Queries

In Grafana, you can create custom queries:

```promql
# Average CPU usage over 5 minutes
avg_over_time(gpustack_ui_system_cpu_percent[5m])

# Request rate per minute
rate(gpustack_ui_total_requests[1m])

# Memory usage trend
avg_over_time(gpustack_ui_system_memory_percent[10m])
```

### 2. Alerts

Set up alerts in Grafana for:
- **High CPU Usage**: Alert when CPU > 80%
- **High Memory Usage**: Alert when memory > 90%
- **Service Down**: Alert when `gpustack_ui_up = 0`
- **High Request Rate**: Alert when requests/minute > threshold

### 3. Custom Dashboards

Create additional dashboards for:
- **AI Model Performance**: Track model loading times and usage
- **File Processing**: Monitor upload and processing metrics
- **User Activity**: Track user sessions and interactions
- **Error Rates**: Monitor API error responses

## 🛠️ Troubleshooting

### Common Issues

1. **Prometheus can't scrape metrics**
   ```bash
   # Check if backend is exposing metrics
   curl http://localhost:8001/api/prometheus
   ```

2. **Grafana can't connect to Prometheus**
   ```bash
   # Check Prometheus is running
   docker-compose -f docker-compose.mac-prod.yml logs prometheus
   ```

3. **No data in dashboards**
   - Check Prometheus targets: http://localhost:9090/targets
   - Verify metrics endpoint: http://localhost:8001/api/prometheus
   - Check Grafana datasource configuration

### Useful Commands

```bash
# View Prometheus targets
curl http://localhost:9090/api/v1/targets

# Check specific metrics
curl http://localhost:8001/api/prometheus | grep gpustack_ui_up

# View Grafana logs
docker-compose -f docker-compose.mac-prod.yml logs grafana

# Restart monitoring services
docker-compose -f docker-compose.mac-prod.yml restart prometheus grafana
```

## 📈 Performance Insights

### What to Monitor

1. **System Resources**
   - CPU usage should stay below 80%
   - Memory usage should stay below 90%
   - Available memory should be > 1GB

2. **Application Performance**
   - Request rate should be stable
   - Response times should be consistent
   - Error rates should be low (< 1%)

3. **User Experience**
   - Active connections should match expected usage
   - Uptime should be > 99.9%
   - Database should always be healthy

### Capacity Planning

Based on your metrics:
- **Light Usage**: 100-200 concurrent users
- **Medium Usage**: 50-100 concurrent users  
- **Heavy Usage**: 20-50 concurrent users

Monitor these thresholds and scale accordingly.

## 🔧 Configuration Files

### Prometheus Configuration
- **File**: `monitoring/prometheus.yml`
- **Scrape Interval**: 15-30 seconds
- **Targets**: Backend health, metrics, and auth endpoints

### Grafana Configuration
- **Dashboards**: `monitoring/grafana/provisioning/dashboards/`
- **Datasources**: `monitoring/grafana/provisioning/datasources/`
- **Auto-provisioning**: Enabled for easy setup

## 🎯 Best Practices

1. **Regular Monitoring**: Check dashboards daily
2. **Alert Setup**: Configure alerts for critical metrics
3. **Data Retention**: Keep metrics for at least 30 days
4. **Backup**: Regularly backup Grafana dashboards
5. **Documentation**: Document custom queries and alerts

## 🚀 Next Steps

1. **Set up alerts** for critical thresholds
2. **Create custom dashboards** for specific use cases
3. **Monitor AI model performance** and usage patterns
4. **Track user behavior** and feature usage
5. **Plan capacity** based on usage trends

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review logs: `docker-compose logs [service-name]`
3. Verify configuration files
4. Test endpoints manually with curl

---

**Happy Monitoring! 🎉**

Your GPUStack UI is now fully monitored with professional-grade observability tools. 