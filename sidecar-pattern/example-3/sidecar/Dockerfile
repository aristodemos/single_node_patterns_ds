FROM alpine:3.19

# Install git
RUN apk add --no-cache git bash

# WORKDIR /shared
WORKDIR /app
# Copy the sync script
COPY sync.sh .
RUN chmod +x sync.sh

# Run the script
CMD ["/usr/local/bin/sync.sh"]
