# Installation Python3.8.10
```sh
# 1. Install dependecies
sudo apt install -y build-essential zlib1g-dev libssl-dev openssl


# 2. Install source code
cd /usr/src
sudo wget https://www.python.org/ftp/python/3.8.10/Python-3.8.10.tgz

# 3. Decompress sorce code
sudo tar xzf Python-3.8.10.tgz
cd Python-3.8.10

# 4. Configure
sudo ./configure \
  --enable-optimizations \
  --prefix=/opt/python3.8


# 5. Build binary
sudo make -j$(nproc)

# 6. Install as alt binary
sudo make altinstall


# 7. Verification
/opt/python3.8/bin/python3.8 --version

# 8. Final
sudo ln -s /opt/python3.8/bin/python3.8 /usr/local/bin/python3.8
python3.8 --version

```
