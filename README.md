## Documentation: Integration of Unimus Devices with MRTG Graphs

### Overview
This application retrieves a list of devices from Unimus via REST API, generates MRTG configurations for each device, and updates MRTG to enable monitoring and graph generation.

The application runs as a Docker container, uses `cron` for periodic updates, and supports both HTTP and HTTPS. Configuration is managed through environment variables, and the container includes persistent volumes for MRTG configurations and data.

---

### Key Features
- **Device retrieval** from Unimus API.
- **MRTG configuration generation** for each device.
- **Automatic MRTG configuration backup** before updates.
- **HTTPS support** for the web interface.
- **Fully configurable** via environment variables.

---

### Environment Configuration
The following environment variables are available for application configuration:

| Variable         | Description                          | Default Value                 |
|-------------------|--------------------------------------|-------------------------------|
| `URL`            | Unimus server API URL               | `http://example.unimus`      |
| `BEARER_TOKEN`   | Bearer token for authentication      | `insert_your_bearer_token`   |
| `Community`      | SNMP community                      | `public`                     |


---

### Persistent Volumes
- **Configuration files:** `/etc/mrtg` (bind-mounted in the container).
- **Data and generated graphs:** `/var/www/html/mrtg` (bind-mounted in the container).

---

### Application Workflow
#### Main Application Code
1. Retrieve a list of devices from the Unimus API.
2. Generate MRTG configuration:
   - Prepare backups of existing configurations.
   - Generate `cfgmaker` commands for each device.
   - Use `indexmaker` to update graphs.
3. Update MRTG configuration and restart MRTG.

#### Dockerfile
- Based on `Ubuntu 22.04`.
- Includes installation of:
  - `mrtg`, `apache2`, `python3`, `snmp`.
- Configures HTTPS for Apache:
  - SSL certificate is generated during the build process.
- Sets up `cron` jobs for periodic application execution.

#### Cron Jobs
- **Every 5 minutes:**
  - Run the main Python script to update MRTG configuration.
  - Execute `mrtg` to apply the changes.

---

### Deployment
1. **Build the container:**
   ```bash
   docker build -t unimus-mrtg .
   ```
2. **Run the container:**
   ```bash
   docker run -d \
     -p 80:80 -p 443:443 \
     -v /path/to/config:/etc/mrtg \
     -v /path/to/data:/var/www/html/mrtg \
     --env-file .env \
     --name unimus-mrtg \
     unimus-mrtg
   ```

---

### Debugging and Logging
- **Application logs:** `/var/log/mrtg_update.log`
- **MRTG logs:** `/var/log/mrtg.log`
- **Apache logs:**
  - Access: `/var/log/apache2/access.log`
  - Error: `/var/log/apache2/error.log`

---

### Security Notes
- **HTTPS:** Use a trusted SSL certificate (e.g., from Let's Encrypt) for production deployments.
- **Tokens:** Ensure `BEARER_TOKEN` is securely stored and not exposed in public repositories.

---

### Sample `.env` File
```dotenv
URL=http://example.unimus
BEARER_TOKEN=your_token_here
Community=public
```

---

### Conclusion
This system provides an automated solution for integrating Unimus devices with MRTG for network monitoring. It ensures ease of maintenance and scalability through a Dockerized architecture.

EXAMPLLE: 
![obrazek](https://github.com/user-attachments/assets/4a55fe1a-1011-43d3-9662-c1ae3d31d3e6)

