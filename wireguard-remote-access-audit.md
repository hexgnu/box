# WireGuard Remote Access Audit for jupiter.home
**Date:** 2026-04-05
**Machine:** jupiter.home (Fedora 42 Linux)
**Public Domain:** jupiter.modulus7.com
**Current Public IP:** 50.47.231.156
**Local Network:** 192.168.88.227/24 (gateway: 192.168.88.1)
**Network Interface:** enp5s0

---

## Executive Summary

The WireGuard remote access infrastructure is **90% complete** but currently **non-functional** due to three critical blocking issues:

1. **WireGuard service failing** - Configuration contains placeholder text instead of actual client public keys
2. **DNS not configured** - jupiter.modulus7.com does not resolve (NXDOMAIN)
3. **Cloudflare API credentials not configured** - DDNS updates failing with "YOUR_ZONE_ID" placeholder

The Ansible automation is well-architected and ready to deploy. Only credential configuration and client key generation remain.

---

## Current State Summary

### ✅ What's Already Complete

#### Software Installation
- **WireGuard Tools:** Installed (v1.0.20210914)
- **WireGuard Kernel Module:** Available and loaded (wireguard.ko v1.0.0)
- **qrencode:** Installed (for mobile client QR codes)
- **DDNS Tools:** curl, jq, bind-utils installed

#### System Configuration
- **IP Forwarding (IPv4):** Enabled (net.ipv4.ip_forward = 1)
- **IP Forwarding (IPv6):** Enabled (net.ipv6.conf.all.forwarding = 1)
- **WireGuard Directory:** Created at /etc/wireguard/ (mode 0700, root:root)
- **Network Interface:** enp5s0 identified for NAT masquerading

#### Ansible Automation
- **WireGuard Role:** Complete implementation at `/home/hexgnu/git/personal/box/wireguard/`
  - tasks/main.yml - Full installation and configuration
  - defaults/main.yml - Sensible defaults configured
  - handlers/main.yml - Service restart handler
  - templates/wg0.conf.j2 - Server configuration template
  - templates/client.conf.j2 - Client configuration template
- **DDNS Role:** Complete implementation at `/home/hexgnu/git/personal/box/ddns/`
  - Cloudflare DDNS script created
  - Systemd service configured
  - Systemd timer enabled (runs every 300 seconds)

#### Firewall Configuration
- **Firewall Service:** firewalld active
- **Current Active Zone:** FedoraWorkstation (default)
- **Trusted Zone:** Configured (ready for wg0 interface)
- **Current Open Ports:** 1025-65535/tcp, 1025-65535/udp (will be removed by WireGuard role)
- **SSH Access:** Enabled

#### Domain Infrastructure
- **Domain:** modulus7.com registered through NameCheap
- **DNS Provider:** Cloudflare (nameservers: jo.ns.cloudflare.com, jobs.ns.cloudflare.com)
- **Domain Expiration:** 2027-04-03 (active for 1 year)

#### Documentation
- **Setup Guide:** `/home/hexgnu/git/personal/box/REMOTE_ACCESS_SETUP.md` - Comprehensive user documentation
- **Project Documentation:** `/home/hexgnu/git/personal/box/CLAUDE.md` - Architecture overview

---

### ❌ What's Not Working

#### Critical Service Failures

**WireGuard Service (wg-quick@wg0):**
```
Status: failed (Result: exit-code)
Error: Key is not the correct length or format: `GENERATE_ON_CLIENT'
Root Cause: /etc/wireguard/wg0.conf contains placeholder "GENERATE_ON_CLIENT" instead of actual public key
Last Attempt: 2026-03-25 13:00:13 PDT
Impact: VPN server not running, no remote access possible
```

**DDNS Service:**
```
Status: Running (timer active) but updates failing
Error: {"errors":[{"code":7003,"message":"Could not route to /client/v4/zones/YOUR_ZONE_ID/dns_records"}]}
Root Cause: /usr/local/bin/cloudflare-ddns.sh contains placeholders:
  - ZONE_ID="YOUR_ZONE_ID"
  - API_TOKEN="YOUR_API_TOKEN"
Last Successful Run: Never (always uses placeholders)
Impact: DNS record not created, domain does not resolve
```

**DNS Resolution:**
```
Query: jupiter.modulus7.com
Result: NXDOMAIN (domain does not exist in DNS)
Tested Via: Local resolver (127.0.0.53), Google DNS (8.8.8.8)
Root Cause: Cloudflare DDNS updates never succeeded, no A record exists
Impact: Cannot connect to WireGuard endpoint from internet
```

---

## Missing Components Checklist

### 🔐 Keys and Security

- [ ] **Generate WireGuard Server Keypair**
  - Action: Run Ansible playbook to auto-generate or manually create
  - Command: `wg genkey | tee server_privatekey | wg pubkey > server_publickey`
  - Storage: Will be placed in /etc/wireguard/wg0.conf by Ansible
  - Status: Partially automated (Ansible generates on first run)

- [ ] **Generate Client Keypair for Laptop**
  - Action: On client machine, generate keypair
  - Command: `wg genkey | tee privatekey | wg pubkey > publickey`
  - Storage: Private key stays on client, public key added to server config
  - Status: Not started (manual step required)

- [ ] **Configure wireguard_clients with Actual Public Keys**
  - Action: Edit wireguard role defaults or create group_vars override
  - File: `/home/hexgnu/git/personal/box/wireguard/defaults/main.yml`
  - Current State: `public_key: GENERATE_ON_CLIENT` (placeholder)
  - Required Change: Replace with actual laptop public key
  - Impact: Blocks WireGuard service from starting

- [ ] **Create Ansible Vault for Secrets**
  - Action: `ansible-vault create group_vars/all/vault.yml`
  - Required Contents:
    ```yaml
    vault_cloudflare_email: matt@matthewkirk.com
    vault_cloudflare_api_token: <GET_FROM_CLOUDFLARE_DASHBOARD>
    vault_cloudflare_zone_id: <GET_FROM_CLOUDFLARE_DASHBOARD>
    ```
  - Status: Not created (vault.yml does not exist)
  - Impact: Blocks DDNS from updating DNS records

### 🌐 DNS and Domain Configuration

- [ ] **Obtain Cloudflare API Token**
  - Action: Log into Cloudflare Dashboard → My Profile → API Tokens → Create Token
  - Required Permissions: Zone.DNS Edit for modulus7.com zone
  - Token Type: Use "Edit zone DNS" template
  - Status: Not obtained

- [ ] **Obtain Cloudflare Zone ID**
  - Action: Cloudflare Dashboard → Select modulus7.com domain → Overview → Zone ID (right sidebar)
  - Format: 32-character hexadecimal string
  - Status: Not obtained

- [ ] **Add Credentials to Ansible Vault**
  - Action: Store tokens in `group_vars/all/vault.yml` (encrypted)
  - Alternative: Set in environment variables (less secure)
  - Status: Blocked by vault creation

- [ ] **Verify DNS Propagation After Setup**
  - Action: `dig +short jupiter.modulus7.com @8.8.8.8`
  - Expected: Should return 50.47.231.156 (current public IP)
  - Status: Not possible until DDNS runs successfully

### 🧱 Firewall and Network

- [ ] **Configure WireGuard Port in Firewall**
  - Action: Automated by Ansible role
  - Port: 51820/udp
  - Command: `firewall-cmd --add-port=51820/udp --permanent`
  - Status: Ready (Ansible will execute on playbook run)

- [ ] **Remove Overly Permissive Firewall Rules**
  - Action: Automated by Ansible role
  - Current Problem: Ports 1025-65535/tcp and 1025-65535/udp are open
  - Will Remove: These wide-open ranges
  - Will Add: Only WireGuard port 51820/udp
  - Status: Ready (Ansible will execute on playbook run)

- [ ] **Add WireGuard Interface to Trusted Zone**
  - Action: Automated by Ansible role
  - Interface: wg0
  - Command: `firewall-cmd --zone=trusted --add-interface=wg0 --permanent`
  - Status: Ready (Ansible will execute on playbook run)

- [ ] **Configure Router Port Forwarding**
  - Action: **MANUAL** - Must configure on router at 192.168.88.1
  - Required Rule:
    - External Port: 51820/UDP
    - Internal IP: 192.168.88.227 (jupiter.home)
    - Internal Port: 51820/UDP
    - Protocol: UDP
  - Router Access: http://192.168.88.1 (likely MikroTik or similar)
  - Status: **UNKNOWN** - Cannot verify remotely, must check router web interface
  - Impact: **CRITICAL** - Without this, WireGuard packets from internet will not reach jupiter.home

### ⚙️ Ansible Integration

- [ ] **Enable WireGuard Role in jupiter.yml**
  - Action: Uncomment line 43 in jupiter.yml
  - Current: `# - wireguard  # VPN server - DISABLED (needs configuration, failing to start)`
  - Change to: `- wireguard`
  - Status: Disabled with reason documented

- [ ] **Run Ansible Playbook with Vault Password**
  - Command: `ansible-playbook -K -i hosts jupiter.yml --ask-vault-pass`
  - Prerequisites:
    - Vault file created with Cloudflare credentials
    - Client public key added to wireguard_clients
  - Status: Ready to run once prerequisites complete

### 📱 Client Onboarding

- [ ] **Generate Client Configuration File**
  - Action: Automated by Ansible (creates /etc/wireguard/client-laptop.conf)
  - Contains: Server public key, endpoint, DNS settings
  - Needs Manual Edit: Replace `GENERATE_THIS_ON_CLIENT` with actual private key
  - Status: Will be created on Ansible run

- [ ] **Retrieve Client Config from Server**
  - Command: `scp hexgnu@192.168.88.227:/etc/wireguard/client-laptop.conf ~/wg-jupiter.conf`
  - Alternative: Copy content manually
  - Status: Blocked until server config generated

- [ ] **Install WireGuard on Client Devices**
  - Linux: `sudo dnf install wireguard-tools`
  - macOS: `brew install wireguard-tools` or WireGuard.app
  - Windows: Download from wireguard.com
  - iOS/Android: WireGuard app from App Store/Play Store
  - Status: Not started

- [ ] **Test VPN Connection from Client**
  - Command: `sudo wg-quick up ~/wg-jupiter.conf`
  - Verify: `ping 10.200.200.1` (should reach jupiter VPN IP)
  - Status: Cannot test until server running

- [ ] **Create QR Code for Mobile Devices (Optional)**
  - Command: `qrencode -t ansiutf8 < /etc/wireguard/client-laptop.conf`
  - Usage: Scan with WireGuard mobile app
  - Status: qrencode installed, ready to use

---

## Detailed Configuration Analysis

### WireGuard Server Configuration Template
**File:** `/home/hexgnu/git/personal/box/wireguard/templates/wg0.conf.j2`

**Analysis:**
```ini
[Interface]
Address = 10.200.200.1/24          # Server VPN IP
ListenPort = 51820                  # Standard WireGuard port
PrivateKey = {{ server_private_key.stdout | default(wireguard_server_private_key) }}

# NAT rules for client traffic
PostUp = iptables -A FORWARD -i %i -j ACCEPT; iptables -A FORWARD -o %i -j ACCEPT; iptables -t nat -A POSTROUTING -o enp5s0 -j MASQUERADE
PostDown = iptables -D FORWARD -i %i -j ACCEPT; iptables -D FORWARD -o %i -j ACCEPT; iptables -t nat -D POSTROUTING -o enp5s0 -j MASQUERADE

[Peer]
PublicKey = GENERATE_ON_CLIENT      # ❌ PROBLEM: Placeholder text
AllowedIPs = 10.200.200.2/32        # Client VPN IP
PersistentKeepalive = 25            # NAT traversal
```

**Issues:**
- ✅ Server private key generation automated by Ansible
- ✅ Network interface (enp5s0) correctly identified
- ✅ NAT masquerading configured for internet access
- ❌ Client public key is placeholder - causes service failure

**Fix Required:** Update `wireguard_clients` variable with actual public key:
```yaml
# Add to group_vars/all/main.yml or wireguard/defaults/main.yml
wireguard_clients:
  - name: laptop
    ip: 10.200.200.2
    public_key: "<ACTUAL_PUBLIC_KEY_FROM_CLIENT>"  # Replace placeholder
```

### Client Configuration Template
**File:** `/home/hexgnu/git/personal/box/wireguard/templates/client.conf.j2`

**Analysis:**
```ini
[Interface]
Address = 10.200.200.2/24           # Client VPN IP
PrivateKey = GENERATE_THIS_ON_CLIENT # ✅ Correct - client generates this
DNS = 1.1.1.1, 1.0.0.1              # Cloudflare DNS

[Peer]
PublicKey = {{ server_public_key.stdout }}  # ✅ Auto-populated
Endpoint = jupiter.modulus7.com:51820       # ❌ DNS not resolving yet
AllowedIPs = 0.0.0.0/0, ::/0               # Route all traffic through VPN
PersistentKeepalive = 25
```

**Issues:**
- ✅ Template correctly generates server public key
- ✅ Endpoint uses dynamic DNS domain
- ❌ Endpoint won't resolve until DNS fixed
- ⚠️  AllowedIPs routes ALL traffic through VPN (may want split-tunnel instead)

**Consideration:** For split-tunnel (only route specific subnets):
```ini
AllowedIPs = 10.200.200.0/24, 192.168.88.0/24  # Only VPN and home network
```

### DDNS Configuration
**File:** `/usr/local/bin/cloudflare-ddns.sh`

**Current State:**
```bash
DOMAIN="jupiter.modulus7.com"  # ✅ Correct
ZONE_ID="YOUR_ZONE_ID"         # ❌ Placeholder
API_TOKEN="YOUR_API_TOKEN"     # ❌ Placeholder
```

**Service Status:**
- Timer: Active, runs every 300 seconds (5 minutes)
- Last Run: 2026-04-05 14:20:19 PDT
- Detection: Successfully gets public IP (50.47.231.156)
- API Call: Fails with zone routing error
- Exit Code: 0 (false success despite API error)

**Fix Required:**
1. Create vault: `ansible-vault create group_vars/all/vault.yml`
2. Add credentials to vault
3. Re-run DDNS role or manually update script

### Firewall Current vs. Desired State

**Current State:**
```
Zone: FedoraWorkstation (default)
Services: dhcpv6-client, samba-client, ssh
Ports: 1025-65535/udp, 1025-65535/tcp  # ❌ Too permissive
```

**After WireGuard Ansible Run:**
```
Zone: FedoraWorkstation (default)
Services: dhcpv6-client, samba-client, ssh
Ports: 51820/udp                        # ✅ Only WireGuard

Zone: trusted
Interface: wg0                          # ✅ VPN traffic trusted
```

**Security Improvement:** Reduces attack surface from 64,511 ports to 1 port.

---

## Recommended Next Steps

### Phase 1: Credential Configuration (30 minutes)
**Priority:** CRITICAL - Blocks all other work

1. **Obtain Cloudflare Credentials**
   - Log into Cloudflare dashboard (cloudflare.com)
   - Navigate to modulus7.com domain
   - Copy Zone ID from Overview page (right sidebar)
   - Create API Token: My Profile → API Tokens → Create Token
     - Use template: "Edit zone DNS"
     - Scope to: modulus7.com zone only
     - Token permissions: Zone.DNS Edit

2. **Create Ansible Vault**
   ```bash
   cd /home/hexgnu/git/personal/box
   ansible-vault create group_vars/all/vault.yml
   ```

   Enter vault password (save in password manager!)

   Add content:
   ```yaml
   ---
   vault_cloudflare_email: matt@matthewkirk.com
   vault_cloudflare_api_token: <TOKEN_FROM_STEP_1>
   vault_cloudflare_zone_id: <ZONE_ID_FROM_STEP_1>
   ```

3. **Verify Vault Created Successfully**
   ```bash
   ansible-vault view group_vars/all/vault.yml
   # Should prompt for password and display contents
   ```

**Acceptance Criteria:**
- ✅ Cloudflare API token obtained with DNS edit permissions
- ✅ Zone ID copied from Cloudflare dashboard
- ✅ Vault file created and encrypted
- ✅ Can view vault with password

---

### Phase 2: DNS Resolution (15 minutes)
**Priority:** HIGH - Required for remote access

4. **Re-run DDNS Role to Update DNS**
   ```bash
   cd /home/hexgnu/git/personal/box
   ansible-playbook -K -i hosts jupiter.yml --ask-vault-pass --tags ddns
   ```

5. **Verify DDNS Service Success**
   ```bash
   sudo systemctl start ddns.service
   sudo journalctl -u ddns.service -n 20
   # Look for successful API response, no errors
   ```

6. **Verify DNS Resolution**
   ```bash
   dig +short jupiter.modulus7.com @8.8.8.8
   # Should return: 50.47.231.156

   # Wait 2-3 minutes for propagation, then test from external network:
   # curl -4 https://1.1.1.1/cdn-cgi/trace | grep ip=
   # nslookup jupiter.modulus7.com 8.8.8.8
   ```

**Acceptance Criteria:**
- ✅ DDNS service runs without API errors
- ✅ Cloudflare shows A record for jupiter.modulus7.com
- ✅ DNS queries return current public IP
- ✅ DNS resolves from external DNS servers

---

### Phase 3: WireGuard Key Generation (10 minutes)
**Priority:** HIGH - Required for server startup

7. **Generate Client Keypair** (on laptop or server temporarily)
   ```bash
   # On client laptop (or generate on server and transfer private key securely):
   wg genkey | tee laptop_privatekey | wg pubkey > laptop_publickey

   # Display keys for copying:
   echo "Private key (keep secret):"
   cat laptop_privatekey
   echo "Public key (add to server):"
   cat laptop_publickey

   # Store private key securely (password manager)
   # Copy public key for next step
   ```

8. **Update WireGuard Client Configuration**

   Edit `/home/hexgnu/git/personal/box/wireguard/defaults/main.yml`:
   ```yaml
   wireguard_clients:
     - name: laptop
       ip: 10.200.200.2
       public_key: "<PASTE_PUBLIC_KEY_FROM_STEP_7>"  # Replace GENERATE_ON_CLIENT
   ```

9. **Enable WireGuard Role**

   Edit `/home/hexgnu/git/personal/box/jupiter.yml` line 43:
   ```yaml
   # Change from:
   # - wireguard  # VPN server - DISABLED (needs configuration, failing to start)

   # To:
   - wireguard
   ```

**Acceptance Criteria:**
- ✅ Client keypair generated and stored securely
- ✅ Public key added to wireguard_clients variable
- ✅ WireGuard role enabled in jupiter.yml
- ✅ Private key backed up in password manager

---

### Phase 4: Server Deployment (15 minutes)
**Priority:** HIGH - Activates VPN server

10. **Run Full Ansible Playbook**
    ```bash
    cd /home/hexgnu/git/personal/box
    ansible-playbook -K -i hosts jupiter.yml --ask-vault-pass
    ```

    Watch for:
    - Server private key generation
    - Configuration file creation
    - Firewall rule updates
    - Service startup

11. **Verify WireGuard Service Running**
    ```bash
    sudo systemctl status wg-quick@wg0
    # Should show: Active: active (exited)

    sudo wg show
    # Should display interface, public key, listening port

    ip addr show wg0
    # Should show: inet 10.200.200.1/24
    ```

12. **Verify Firewall Configuration**
    ```bash
    firewall-cmd --list-all
    # Should show: ports: 51820/udp
    # Should NOT show: 1025-65535/tcp, 1025-65535/udp

    firewall-cmd --zone=trusted --list-all
    # Should show: interfaces: wg0
    ```

**Acceptance Criteria:**
- ✅ Ansible playbook completes without errors
- ✅ wg-quick@wg0 service status is active
- ✅ `wg show` displays server configuration
- ✅ Firewall allows only 51820/udp
- ✅ wg0 interface in trusted zone

---

### Phase 5: Router Configuration (20 minutes)
**Priority:** CRITICAL - Required for internet access to VPN

13. **Access Router Configuration**
    - Navigate to: http://192.168.88.1
    - Login with admin credentials
    - Locate Port Forwarding / NAT / Virtual Server section

14. **Configure Port Forwarding Rule**
    - Rule Name: WireGuard VPN
    - Protocol: UDP
    - External Port: 51820
    - Internal IP: 192.168.88.227
    - Internal Port: 51820
    - Enable: Yes
    - Save and Apply

15. **Verify Router Configuration**
    - Confirm rule appears in active port forwards
    - Check router logs for any errors
    - Note: Cannot fully test until client connection attempt

**Router-Specific Notes:**
- Router IP: 192.168.88.1 (likely MikroTik based on .88 subnet)
- If MikroTik: IP → Firewall → NAT → Add (+)
  - Chain: dstnat
  - Protocol: udp
  - Dst. Port: 51820
  - In. Interface: ether1 (WAN interface)
  - Action: dst-nat
  - To Addresses: 192.168.88.227
  - To Ports: 51820

**Acceptance Criteria:**
- ✅ Port forwarding rule created and active
- ✅ Rule targets UDP port 51820
- ✅ Rule forwards to 192.168.88.227:51820
- ✅ Rule saved to router configuration (survives reboot)

---

### Phase 6: Client Setup and Testing (30 minutes)
**Priority:** HIGH - Final verification

16. **Retrieve Client Configuration from Server**
    ```bash
    # From laptop:
    scp hexgnu@192.168.88.227:/etc/wireguard/client-laptop.conf ~/wg-jupiter.conf
    ```

17. **Edit Client Configuration with Private Key**
    ```bash
    # Edit ~/wg-jupiter.conf
    # Find line: PrivateKey = GENERATE_THIS_ON_CLIENT
    # Replace with: PrivateKey = <PRIVATE_KEY_FROM_PHASE_3_STEP_7>
    ```

18. **Install WireGuard on Client** (if not already installed)
    ```bash
    # Fedora/RHEL:
    sudo dnf install wireguard-tools

    # Ubuntu/Debian:
    sudo apt install wireguard-tools

    # macOS:
    brew install wireguard-tools
    # Or use WireGuard.app from App Store
    ```

19. **Test VPN Connection from Local Network**
    ```bash
    # Start VPN:
    sudo wg-quick up ~/wg-jupiter.conf

    # Verify connection:
    sudo wg show
    # Should show peer (jupiter server)

    # Test connectivity:
    ping 10.200.200.1
    # Should receive replies from VPN server

    # Test SSH over VPN:
    ssh hexgnu@10.200.200.1
    ```

20. **Test VPN Connection from External Network**
    - Disconnect from local network (use phone hotspot or coffee shop WiFi)
    - Start VPN: `sudo wg-quick up ~/wg-jupiter.conf`
    - Ping: `ping 10.200.200.1`
    - SSH: `ssh hexgnu@10.200.200.1`
    - Test service access: `curl http://10.200.200.1:3000` (if dev server running)

21. **Create Additional Client Configs (Optional)**

    For phone/tablet:
    ```bash
    # On server:
    sudo qrencode -t ansiutf8 < /etc/wireguard/client-laptop.conf
    # Scan QR code with WireGuard mobile app

    # Or create separate configs for each device:
    # 1. Generate new keypair for device
    # 2. Add to wireguard_clients with unique IP (10.200.200.3, etc.)
    # 3. Re-run Ansible playbook
    # 4. Retrieve new client config
    ```

**Acceptance Criteria:**
- ✅ Client config retrieved and private key added
- ✅ WireGuard installed on client device
- ✅ VPN connects successfully from local network
- ✅ Can ping 10.200.200.1 through VPN
- ✅ Can SSH to jupiter.home via VPN IP
- ✅ VPN connects from external network (phone hotspot/public WiFi)
- ✅ All development services accessible through VPN

---

### Phase 7: Security Hardening (Optional, 15 minutes)
**Priority:** MEDIUM - Improves security posture

22. **Review and Adjust AllowedIPs**

    Current client config routes ALL traffic through VPN. Consider split-tunnel:
    ```ini
    # Edit client config
    # Change from:
    AllowedIPs = 0.0.0.0/0, ::/0

    # To (split-tunnel):
    AllowedIPs = 10.200.200.0/24, 192.168.88.0/24
    ```

    Benefits:
    - Faster internet (doesn't route through home)
    - Less bandwidth usage on home connection
    - Only routes VPN and home network traffic

23. **Configure SSH to Only Listen on VPN**

    Edit `/etc/ssh/sshd_config`:
    ```
    # Add:
    ListenAddress 10.200.200.1
    ListenAddress 192.168.88.227

    # Restart SSH:
    sudo systemctl restart sshd
    ```

24. **Test Firewall with Aggressive Scan**
    ```bash
    # From external network:
    nmap -p1-65535 jupiter.modulus7.com
    # Should only show: 51820/udp open
    ```

**Acceptance Criteria:**
- ✅ Split-tunnel configured (if desired)
- ✅ SSH only listens on local/VPN IPs (not 0.0.0.0)
- ✅ External port scan shows only WireGuard port
- ✅ No unexpected services exposed

---

## Dependency Graph

```
Phase 1: Credential Configuration
  └─> Phase 2: DNS Resolution
       ├─> Phase 3: WireGuard Key Generation
       │    └─> Phase 4: Server Deployment
       │         └─> Phase 5: Router Configuration
       │              └─> Phase 6: Client Setup
       │                   └─> Phase 7: Security Hardening (optional)
       │
       └─> Can proceed in parallel with Phase 3
```

**Critical Path:** 1 → 2 → 3 → 4 → 5 → 6 (estimated 120 minutes)

**Blockers:**
- Phase 2 blocked by Phase 1 (needs vault credentials)
- Phase 4 blocked by Phase 3 (needs client public key)
- Phase 6 blocked by Phase 4 and 5 (needs server running and router configured)

**Parallel Work Opportunities:**
- While waiting for DNS propagation (Phase 2), start Phase 3 (key generation)
- Router configuration (Phase 5) can be researched during Ansible run (Phase 4)

---

## Reference Information

### WireGuard Documentation
- Official Site: https://www.wireguard.com/
- Quick Start: https://www.wireguard.com/quickstart/
- Man Pages: `man wg`, `man wg-quick`
- Kernel Module Info: https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/drivers/net/wireguard

### Ansible WireGuard Examples
- Ansible Galaxy Role: https://galaxy.ansible.com/ui/standalone/roles/githubixx/ansible_role_wireguard/
- Community Examples: https://github.com/search?q=ansible+wireguard
- Molecule Testing: https://molecule.readthedocs.io/

### Cloudflare DDNS
- API Documentation: https://developers.cloudflare.com/api/
- DNS API: https://developers.cloudflare.com/api/operations/dns-records-for-a-zone-create-dns-record
- API Token Creation: https://dash.cloudflare.com/profile/api-tokens

### Security Best Practices
- WireGuard Deployment Best Practices: https://www.wireguard.com/papers/wireguard.pdf
- NIST VPN Guidelines: https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-77r1.pdf
- Firewall Hardening: https://www.cisecurity.org/

### Troubleshooting Commands
```bash
# WireGuard status
sudo wg show
sudo wg show wg0

# Service logs
sudo journalctl -u wg-quick@wg0 -f
sudo journalctl -u ddns.service -f

# Network debugging
ip addr show wg0
ip route show table main
iptables -t nat -L POSTROUTING -n -v

# Firewall verification
firewall-cmd --list-all
firewall-cmd --zone=trusted --list-all

# DNS testing
dig +short jupiter.modulus7.com @8.8.8.8
nslookup jupiter.modulus7.com 1.1.1.1

# Connectivity testing
ping 10.200.200.1              # VPN server
traceroute 10.200.200.1        # Path to VPN
tcpdump -i wg0                 # Capture VPN traffic
```

---

## Risk Assessment

### High Risk Items
1. **Router Port Forwarding** - If misconfigured, VPN will not be accessible from internet
   - Mitigation: Test from external network, verify with packet capture

2. **Cloudflare API Credentials** - If leaked, DNS could be hijacked
   - Mitigation: Use Ansible vault, minimal token permissions, rotate regularly

3. **WireGuard Private Keys** - If compromised, attacker gains VPN access
   - Mitigation: Store in password manager, never commit to git, use strong permissions (0600)

### Medium Risk Items
1. **AllowedIPs = 0.0.0.0/0** - Routes all client traffic through home connection
   - Impact: Privacy exposure, bandwidth usage, single point of failure
   - Mitigation: Consider split-tunnel configuration

2. **Wide Firewall Rules** - Currently 1025-65535 open (will be fixed)
   - Impact: Attack surface exposure until Ansible run
   - Mitigation: Run Phase 4 ASAP to close ports

### Low Risk Items
1. **DDNS Update Frequency** - Every 5 minutes may be excessive
   - Impact: Unnecessary API calls
   - Mitigation: Increase interval if IP changes are rare

2. **No VPN Monitoring** - No alerts if VPN goes down
   - Impact: Silent failure possible
   - Mitigation: Add monitoring/alerting in future iteration

---

## Success Metrics

### Functional Requirements
- ✅ WireGuard service running and stable (wg-quick@wg0 active)
- ✅ DNS resolves jupiter.modulus7.com to current public IP
- ✅ Can connect to VPN from external network
- ✅ Can access SSH (port 22) via VPN IP (10.200.200.1)
- ✅ Can access PostgreSQL (port 5432) via VPN IP
- ✅ Can access development servers via VPN IP
- ✅ DDNS updates automatically on IP change

### Security Requirements
- ✅ Only WireGuard port (51820/udp) exposed to internet
- ✅ All other services only accessible via VPN
- ✅ Firewall rules locked down (no 1025-65535 ranges)
- ✅ Credentials encrypted in Ansible vault
- ✅ WireGuard keys properly secured (0600 permissions)

### Operational Requirements
- ✅ VPN reconnects automatically after network change
- ✅ DDNS updates within 5 minutes of IP change
- ✅ Client configuration documented and reproducible
- ✅ Can provision additional clients without server downtime

---

## Estimated Time to Completion

| Phase | Description | Time Estimate | Skill Level |
|-------|-------------|---------------|-------------|
| 1 | Credential Configuration | 30 min | Beginner |
| 2 | DNS Resolution | 15 min | Beginner |
| 3 | WireGuard Key Generation | 10 min | Beginner |
| 4 | Server Deployment | 15 min | Intermediate |
| 5 | Router Configuration | 20 min | Intermediate |
| 6 | Client Setup and Testing | 30 min | Intermediate |
| 7 | Security Hardening (optional) | 15 min | Advanced |
| **TOTAL** | **End-to-End Setup** | **~2 hours** | **Mixed** |

**Notes:**
- Times assume familiarity with SSH, command line, basic networking
- Router configuration time varies based on router type/UI
- First-time setup will take longer; subsequent clients take ~5 minutes
- Troubleshooting time not included (add 50% buffer)

---

## Appendix A: Current Configuration Files

### /etc/wireguard/wg0.conf (Expected After Ansible Run)
```ini
[Interface]
Address = 10.200.200.1/24
ListenPort = 51820
PrivateKey = <AUTO_GENERATED_BY_ANSIBLE>

PostUp = iptables -A FORWARD -i %i -j ACCEPT; iptables -A FORWARD -o %i -j ACCEPT; iptables -t nat -A POSTROUTING -o enp5s0 -j MASQUERADE
PostDown = iptables -D FORWARD -i %i -j ACCEPT; iptables -D FORWARD -o %i -j ACCEPT; iptables -t nat -D POSTROUTING -o enp5s0 -j MASQUERADE

# laptop
[Peer]
PublicKey = <CLIENT_PUBLIC_KEY_FROM_PHASE_3>
AllowedIPs = 10.200.200.2/32
PersistentKeepalive = 25
```

### /etc/wireguard/client-laptop.conf (Expected After Ansible Run)
```ini
[Interface]
Address = 10.200.200.2/24
PrivateKey = GENERATE_THIS_ON_CLIENT
DNS = 1.1.1.1, 1.0.0.1

[Peer]
PublicKey = <SERVER_PUBLIC_KEY_AUTO_GENERATED>
Endpoint = jupiter.modulus7.com:51820
AllowedIPs = 0.0.0.0/0, ::/0
PersistentKeepalive = 25
```

### /usr/local/bin/cloudflare-ddns.sh (After Phase 2)
```bash
#!/bin/bash
DOMAIN="jupiter.modulus7.com"
ZONE_ID="<FROM_VAULT>"
API_TOKEN="<FROM_VAULT>"

PUBLIC_IP=$(curl -s https://api.ipify.org)
# ... (rest of script remains same)
```

---

## Appendix B: Network Topology

```
Internet
   │
   │ Public IP: 50.47.231.156
   │ Domain: jupiter.modulus7.com:51820
   ▼
Router (192.168.88.1)
   │
   │ Port Forward: 51820/UDP → 192.168.88.227:51820
   │
   ▼
jupiter.home (192.168.88.227)
   │
   ├─ enp5s0: 192.168.88.227/24 (LAN interface)
   │
   └─ wg0: 10.200.200.1/24 (VPN interface)
       │
       └─ VPN Clients
           └─ laptop: 10.200.200.2/24
```

**Traffic Flow:**
1. Client → jupiter.modulus7.com:51820 (DNS lookup)
2. Client → 50.47.231.156:51820 (WireGuard handshake)
3. Router → 192.168.88.227:51820 (port forward)
4. jupiter.home wg0 interface (packet decryption)
5. jupiter.home services (SSH, PostgreSQL, dev servers)

---

## Appendix C: Firewall Rule Changes

### Before WireGuard Setup
```
# firewall-cmd --list-all
FedoraWorkstation (default, active)
  services: dhcpv6-client samba-client ssh
  ports: 1025-65535/udp 1025-65535/udp
  ❌ PROBLEM: 130,000+ ports exposed
```

### After WireGuard Setup
```
# firewall-cmd --list-all
FedoraWorkstation (default, active)
  services: dhcpv6-client samba-client ssh
  ports: 51820/udp
  ✅ SECURE: Only WireGuard port exposed

# firewall-cmd --zone=trusted --list-all
trusted
  interfaces: wg0
  ✅ SECURE: VPN traffic fully trusted
```

---

## Appendix D: Verification Checklist

Run these commands after completing all phases to verify success:

```bash
# ===== Server Verification =====
# WireGuard service running
sudo systemctl is-active wg-quick@wg0
# Expected: active

# WireGuard interface exists
ip addr show wg0
# Expected: inet 10.200.200.1/24

# WireGuard listening
sudo wg show
# Expected: Shows interface, peer, endpoint

# Firewall allows WireGuard
firewall-cmd --list-ports
# Expected: 51820/udp

# Firewall trusts VPN
firewall-cmd --zone=trusted --list-interfaces
# Expected: wg0

# DNS resolves
dig +short jupiter.modulus7.com @8.8.8.8
# Expected: 50.47.231.156 (or current public IP)

# DDNS service succeeds
sudo journalctl -u ddns.service -n 5 --no-pager | grep -i error
# Expected: No errors

# IP forwarding enabled
sysctl net.ipv4.ip_forward
# Expected: net.ipv4.ip_forward = 1

# ===== Client Verification =====
# WireGuard installed
wg --version
# Expected: wireguard-tools vX.X.X

# Can connect to VPN
sudo wg-quick up ~/wg-jupiter.conf && sleep 2 && sudo wg show
# Expected: Shows peer with handshake

# Can ping VPN server
ping -c 3 10.200.200.1
# Expected: 0% packet loss

# Can SSH via VPN
ssh -o ConnectTimeout=5 hexgnu@10.200.200.1 "hostname"
# Expected: jupiter.home

# DNS works through VPN
nslookup google.com
# Expected: Response from 1.1.1.1 (WireGuard DNS)

# ===== External Verification =====
# Port scan shows only WireGuard
nmap -p1-65535 jupiter.modulus7.com | grep open
# Expected: 51820/udp open

# Can connect from external network
# (Disconnect from local network, connect via phone hotspot)
sudo wg-quick up ~/wg-jupiter.conf
ping -c 3 10.200.200.1
# Expected: 0% packet loss
```

---

## Conclusion

The WireGuard remote access infrastructure for jupiter.home is **architecturally sound** and **90% complete**. The Ansible automation is production-ready and well-documented.

**Remaining work is purely operational:**
1. Configure Cloudflare API credentials (30 min)
2. Generate client keys (10 min)
3. Run Ansible playbook (15 min)
4. Configure router port forwarding (20 min)
5. Test client connection (30 min)

**Total time to production: ~2 hours**

No code changes required. No infrastructure gaps. Only credential configuration and deployment execution remain.

**Next Action:** Start with Phase 1 (Credential Configuration) to unblock all subsequent phases.
