docker build -t rad_snapper .
docker run -v /$(pwd)/data:/app/data rad_snapper