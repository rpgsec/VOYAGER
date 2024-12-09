# Voyager

Voyager is an exploration and reconnaissance system.

# Wishlist Comes here: 

## Prerequisites

For the installation, it's essential to have a properly set-up Go environment. If not, you can follow the [installation instructions](https://golang.org/doc/install) on the official Go website.

## Installation Steps

Proceed with the installation of the following components:

### 1. Subfinder

Subfinder, a subdomain discovery tool, can be installed using:

```
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
```
Refer to the official Subfinder [GitHub repository](https://github.com/projectdiscovery/subfinder) for additional details.

### 2. Naabu
Install Naabu, a port scanning tool, using:
```
go install -v github.com/projectdiscovery/naabu/v2/cmd/naabu@latest
```
Visit Naabu's [GitHub repository](https://github.com/projectdiscovery/naabu) for more info.

### 3. Httprobe
Httprobe is useful for live web servers. Install it with:
```
go install github.com/tomnomnom/httprobe@latest
```
Further details can be found at Httprobe's [GitHub repository](https://github.com/tomnomnom/httprobe).


### 4. Fuff
Fast web fuzzer (FFUF), a valuable testing tool, can be installed using:
```
go install github.com/ffuf/ffuf/v2@latest
```
Visit FFUF's [GitHub repository](https://github.com/ffuf/ffuf) for more information.


### 5. Waybackurls
To fetch all the URLs a website has had, install Waybackurls:
```
go install github.com/tomnomnom/waybackurls@latest
```
More about Waybackurls can be found on its [official GitHub repository.](https://github.com/tomnomnom/waybackurls)
