#!/usr/bin/env python3
"""
VHost Configuration Tester for ZeroLinkChain
Tests and validates Apache virtual host configurations
"""

import os
import sys
import subprocess
import requests
import json
import time
from pathlib import Path

class VHostTester:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.successes = []
        
    def run_tests(self):
        """Run comprehensive vhost tests"""
        print("🔍 ZEROLINKCHAIN VHOST CONFIGURATION TESTER")
        print("=" * 60)
        
        # Test 1: Check Apache modules
        self.check_apache_modules()
        
        # Test 2: Validate vhost configurations
        self.validate_vhost_configs()
        
        # Test 3: Test endpoints
        self.test_endpoints()
        
        # Test 4: Check file permissions
        self.check_permissions()
        
        # Test 5: Test downloads directory
        self.test_downloads()
        
        # Test 6: API proxy test
        self.test_api_proxy()
        
        # Generate report
        self.generate_report()
        
    def check_apache_modules(self):
        """Check and enable required Apache modules"""
        print("\n📦 APACHE MODULE CHECK")
        print("-" * 40)
        
        required_modules = {
            'proxy': 'Enables proxy functionality',
            'proxy_http': 'HTTP proxy support',
            'rewrite': 'URL rewriting',
            'headers': 'Header manipulation',
            'ssl': 'SSL/TLS support'
        }
        
        # Check current modules
        try:
            result = subprocess.run(['apache2ctl', '-M'], 
                                  capture_output=True, text=True)
            enabled_modules = result.stdout
            
            for module, description in required_modules.items():
                if f"{module}_module" in enabled_modules:
                    self.successes.append(f"✅ Module {module}: Already enabled")
                    print(f"✅ {module}: Already enabled - {description}")
                else:
                    self.warnings.append(f"⚠️ Module {module}: Not enabled")
                    print(f"⚠️ {module}: NOT ENABLED - {description}")
                    print(f"   To enable: sudo a2enmod {module}")
                    
        except Exception as e:
            self.errors.append(f"Failed to check modules: {e}")
            print(f"❌ Could not check modules: {e}")
    
    def validate_vhost_configs(self):
        """Validate vhost configuration syntax"""
        print("\n🔧 VHOST CONFIGURATION VALIDATION")
        print("-" * 40)
        
        vhost_files = [
            '/etc/apache2/sites-available/dev.zerolinkchain.com.conf',
            '/etc/apache2/sites-available/dev.zerolinkchain.com-improved.conf',
            '/etc/apache2/sites-available/main.conf'
        ]
        
        for vhost in vhost_files:
            if os.path.exists(vhost):
                try:
                    # Test configuration syntax
                    result = subprocess.run(['apache2ctl', '-t', '-f', vhost],
                                          capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        self.successes.append(f"✅ {os.path.basename(vhost)}: Valid syntax")
                        print(f"✅ {os.path.basename(vhost)}: Syntax OK")
                    else:
                        self.errors.append(f"❌ {os.path.basename(vhost)}: Syntax error")
                        print(f"❌ {os.path.basename(vhost)}: Syntax error")
                        print(f"   Error: {result.stderr}")
                except Exception as e:
                    self.warnings.append(f"Could not validate {vhost}: {e}")
                    print(f"⚠️ Could not validate {os.path.basename(vhost)}: {e}")
            else:
                print(f"⏭️ {os.path.basename(vhost)}: Not found")
    
    def test_endpoints(self):
        """Test various deployment endpoints"""
        print("\n🌐 ENDPOINT TESTING")
        print("-" * 40)
        
        endpoints = [
            ('http://localhost/', 'Main site'),
            ('http://localhost/dashboard.html', 'Dashboard'),
            ('http://localhost/test_monitoring.html', 'Test monitoring'),
            ('http://localhost/CLIENT_TESTING_GUIDE.md', 'Client guide'),
            ('http://localhost/downloads/', 'Downloads directory'),
            ('http://localhost:5000/api/v1/status', 'API status (direct)'),
            ('http://localhost/api/v1/status', 'API status (proxied)')
        ]
        
        for url, description in endpoints:
            try:
                response = requests.get(url, timeout=5, allow_redirects=True)
                
                if response.status_code == 200:
                    self.successes.append(f"✅ {description}: Accessible")
                    print(f"✅ {description}: {response.status_code} OK")
                    
                    # Check for development headers
                    if 'X-Development-Environment' in response.headers:
                        print(f"   Dev header: {response.headers['X-Development-Environment']}")
                        
                elif response.status_code == 404:
                    self.warnings.append(f"⚠️ {description}: Not found")
                    print(f"⚠️ {description}: 404 Not Found")
                else:
                    self.warnings.append(f"⚠️ {description}: HTTP {response.status_code}")
                    print(f"⚠️ {description}: HTTP {response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                self.errors.append(f"❌ {description}: Connection failed")
                print(f"❌ {description}: Connection failed")
            except requests.exceptions.Timeout:
                self.errors.append(f"❌ {description}: Timeout")
                print(f"❌ {description}: Timeout")
            except Exception as e:
                self.errors.append(f"❌ {description}: {e}")
                print(f"❌ {description}: {e}")
    
    def check_permissions(self):
        """Check file and directory permissions"""
        print("\n🔒 PERMISSIONS CHECK")
        print("-" * 40)
        
        paths_to_check = [
            ('/var/www/html', '755', 'Document root'),
            ('/var/www/html/downloads', '755', 'Downloads directory'),
            ('/var/www/html/data', '750', 'Data directory'),
            ('/var/log/apache2', '755', 'Apache logs')
        ]
        
        for path, expected_perms, description in paths_to_check:
            if os.path.exists(path):
                try:
                    stat_info = os.stat(path)
                    current_perms = oct(stat_info.st_mode)[-3:]
                    
                    if current_perms == expected_perms:
                        self.successes.append(f"✅ {description}: Correct permissions")
                        print(f"✅ {description}: {current_perms} (correct)")
                    else:
                        self.warnings.append(f"⚠️ {description}: Wrong permissions")
                        print(f"⚠️ {description}: {current_perms} (expected {expected_perms})")
                        
                except Exception as e:
                    self.errors.append(f"Could not check {path}: {e}")
                    print(f"❌ Could not check {description}: {e}")
            else:
                self.warnings.append(f"⚠️ {description}: Does not exist")
                print(f"⚠️ {description}: Does not exist")
    
    def test_downloads(self):
        """Test downloads directory and files"""
        print("\n📥 DOWNLOADS DIRECTORY TEST")
        print("-" * 40)
        
        download_files = [
            'quick-deploy.sh',
            'zerolinkchain-vpn-linux.sh',
            'zerolinkchain-client.py'
        ]
        
        downloads_dir = '/var/www/html/downloads'
        
        if os.path.exists(downloads_dir):
            for filename in download_files:
                filepath = os.path.join(downloads_dir, filename)
                
                if os.path.exists(filepath):
                    # Check if executable
                    if os.access(filepath, os.X_OK):
                        self.successes.append(f"✅ {filename}: Available and executable")
                        print(f"✅ {filename}: Available and executable")
                    else:
                        self.warnings.append(f"⚠️ {filename}: Not executable")
                        print(f"⚠️ {filename}: Available but not executable")
                else:
                    self.errors.append(f"❌ {filename}: Not found")
                    print(f"❌ {filename}: Not found")
                    
            # Test web access to downloads
            try:
                response = requests.get('http://localhost/downloads/', timeout=5)
                if 'Index of /downloads' in response.text or response.status_code == 200:
                    self.successes.append("✅ Downloads directory listing: Working")
                    print("✅ Downloads directory listing: Accessible via web")
                else:
                    self.warnings.append("⚠️ Downloads directory listing: Not working")
                    print("⚠️ Downloads directory listing: Not properly configured")
            except Exception as e:
                self.errors.append(f"Downloads web access failed: {e}")
                print(f"❌ Downloads web access failed: {e}")
        else:
            self.errors.append("Downloads directory does not exist")
            print(f"❌ Downloads directory does not exist")
    
    def test_api_proxy(self):
        """Test API proxy configuration"""
        print("\n🔌 API PROXY CONFIGURATION TEST")
        print("-" * 40)
        
        # Check if API server is running
        try:
            direct_response = requests.get('http://localhost:5000/api/v1/status', timeout=5)
            
            if direct_response.status_code == 200:
                print("✅ API server running on port 5000")
                
                # Test proxied access
                try:
                    proxy_response = requests.get('http://localhost/api/v1/status', timeout=5)
                    
                    if proxy_response.status_code == 200:
                        self.successes.append("✅ API proxy: Working")
                        print("✅ API proxy: Working correctly")
                        
                        # Compare responses
                        if direct_response.json() == proxy_response.json():
                            print("   ✅ Proxy response matches direct response")
                        else:
                            self.warnings.append("Proxy response differs from direct")
                            print("   ⚠️ Proxy response differs from direct response")
                            
                    elif proxy_response.status_code == 502:
                        self.errors.append("❌ API proxy: Bad Gateway")
                        print("❌ API proxy: Bad Gateway (502)")
                        print("   Check if proxy modules are enabled")
                    else:
                        self.warnings.append(f"API proxy returned {proxy_response.status_code}")
                        print(f"⚠️ API proxy: HTTP {proxy_response.status_code}")
                        
                except Exception as e:
                    self.errors.append(f"API proxy test failed: {e}")
                    print(f"❌ API proxy test failed: {e}")
                    print("   Proxy modules may not be enabled")
                    
            else:
                self.warnings.append("API server not returning 200")
                print(f"⚠️ API server returned {direct_response.status_code}")
                
        except requests.exceptions.ConnectionError:
            self.warnings.append("API server not running on port 5000")
            print("⚠️ API server not running on port 5000")
            print("   Cannot test proxy without backend")
        except Exception as e:
            self.errors.append(f"API test failed: {e}")
            print(f"❌ API test failed: {e}")
    
    def generate_report(self):
        """Generate final test report"""
        print("\n" + "=" * 60)
        print("📋 VHOST CONFIGURATION TEST REPORT")
        print("=" * 60)
        
        total_tests = len(self.successes) + len(self.warnings) + len(self.errors)
        
        print(f"\n📊 Test Summary:")
        print(f"   ✅ Passed: {len(self.successes)}")
        print(f"   ⚠️ Warnings: {len(self.warnings)}")
        print(f"   ❌ Failed: {len(self.errors)}")
        print(f"   📈 Success Rate: {len(self.successes)/total_tests*100:.1f}%")
        
        if self.errors:
            print(f"\n❌ CRITICAL ISSUES TO FIX:")
            for error in self.errors:
                print(f"   • {error}")
                
        if self.warnings:
            print(f"\n⚠️ WARNINGS TO ADDRESS:")
            for warning in self.warnings:
                print(f"   • {warning}")
        
        print(f"\n💡 RECOMMENDATIONS:")
        
        # Check for proxy module issues
        proxy_modules = ['proxy', 'proxy_http']
        missing_modules = []
        
        for module in proxy_modules:
            if any(f"Module {module}: Not enabled" in w for w in self.warnings):
                missing_modules.append(module)
        
        if missing_modules:
            print(f"\n   1. Enable required Apache modules:")
            for module in missing_modules:
                print(f"      sudo a2enmod {module}")
            print(f"      sudo systemctl reload apache2")
        
        # Check for improved vhost
        if os.path.exists('/etc/apache2/sites-available/dev.zerolinkchain.com-improved.conf'):
            print(f"\n   2. Activate improved vhost configuration:")
            print(f"      sudo a2dissite dev.zerolinkchain.com")
            print(f"      sudo a2ensite dev.zerolinkchain.com-improved")
            print(f"      sudo systemctl reload apache2")
        
        # Check API server
        if any("API server not running" in w for w in self.warnings):
            print(f"\n   3. Start the API server:")
            print(f"      cd /var/www/html")
            print(f"      python3 api_server.py &")
        
        if len(self.errors) == 0:
            print(f"\n🎯 STATUS: VHOST CONFIGURATION READY FOR TESTING! ✅")
        elif len(self.errors) <= 2:
            print(f"\n⚠️ STATUS: MINOR ISSUES - Fix before production deployment")
        else:
            print(f"\n❌ STATUS: CRITICAL ISSUES - Must fix before testing")
        
        # Save report to file
        report_file = '/var/www/html/vhost_test_report.txt'
        with open(report_file, 'w') as f:
            f.write(f"VHOST Configuration Test Report\n")
            f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"=" * 60 + "\n\n")
            
            f.write(f"Summary:\n")
            f.write(f"  Passed: {len(self.successes)}\n")
            f.write(f"  Warnings: {len(self.warnings)}\n")
            f.write(f"  Failed: {len(self.errors)}\n\n")
            
            if self.errors:
                f.write("Critical Issues:\n")
                for error in self.errors:
                    f.write(f"  - {error}\n")
                f.write("\n")
            
            if self.warnings:
                f.write("Warnings:\n")
                for warning in self.warnings:
                    f.write(f"  - {warning}\n")
                f.write("\n")
            
            if self.successes:
                f.write("Successful Tests:\n")
                for success in self.successes:
                    f.write(f"  - {success}\n")
        
        print(f"\n📄 Report saved to: {report_file}")

if __name__ == "__main__":
    tester = VHostTester()
    tester.run_tests()
