# Security Policy

## Supported Versions

We maintain security updates for the following versions of Patchy:

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0.0 | :x:                |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security issue in Patchy:

1. **DO NOT** disclose the vulnerability publicly
2. Please report it through our [GitHub Security Advisories](https://github.com/7eventy7/trackly/security/advisories/new)

### What to Include in Your Report

- Detailed description of the vulnerability
- Steps to reproduce the issue
- Potential impact of the vulnerability
- Suggested fixes (if any)

### Response Timeline

- Initial Response: Within 48 hours
- Status Update: Within 5 business days
- Resolution Timeline: Based on severity and complexity

## Security Considerations

### Docker Socket Access

Patchy requires access to the Docker socket to function. Please be aware of the following:

1. **Socket Permissions**: 
   - Only grant socket access if you trust this application
   - Consider using reduced-privilege alternatives when possible

2. **Container Security**:
   - Run Patchy with minimal required permissions
   - Use read-only access where possible
   - Keep the container updated for security patches

### Best Practices

1. **Stay Updated**:
   - Use the latest version of Patchy
   - Enable automatic updates when possible
   - Watch our release announcements for security updates

2. **Configuration**:
   - Use secure configuration settings
   - Limit network exposure
   - Follow the principle of least privilege

## Security Features

We've implemented the following security measures:
- Read-only Docker socket access
- No permanent data storage
- Regular security updates
- Minimal base image
- Automated vulnerability scanning

## Attribution

We'd like to credit security researchers who report valid vulnerabilities in our security advisories. If you wish to remain anonymous, please indicate this in your report.

---

This security policy is subject to change without notice. Please check back regularly for updates.
