#!/usr/bin/env node

/**
 * 路径配置验证脚本
 * 检查所有 vite.config.js 和构建配置，确保路径配置正确
 * 
 * 注意：移动端项目已独立迁移，此脚本仅验证 PC 端配置
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const projectRoot = path.resolve(__dirname, '..');

const BASE_URL = 'https://yutt.xyz';

// 颜色输出
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

function checkPcViteConfig() {
  const configPath = path.join(projectRoot, 'sau_frontend', 'vite.config.js');
  
  if (!fs.existsSync(configPath)) {
    log(`❌ PC端 vite.config.js 不存在: ${configPath}`, 'red');
    return false;
  }

  const content = fs.readFileSync(configPath, 'utf8');
  let hasAllowedHosts = false;
  let hasCorrectHost = false;

  // 检查是否有 allowedHosts 配置
  if (content.includes('allowedHosts')) {
    hasAllowedHosts = true;
    // 检查是否包含 yutt.xyz
    if (content.includes("'yutt.xyz'") || content.includes('"yutt.xyz"')) {
      hasCorrectHost = true;
    }
  }

  if (!hasAllowedHosts) {
    log(`❌ PC端 vite.config.js 缺少 allowedHosts 配置`, 'red');
    return false;
  }

  if (!hasCorrectHost) {
    log(`❌ PC端 vite.config.js allowedHosts 未包含 'yutt.xyz'`, 'red');
    return false;
  }

  log(`✅ PC端 vite.config.js 配置正确`, 'green');
  return true;
}

function main() {
  log('\n🔍 开始验证路径配置...\n', 'blue');
  log('注意：移动端项目已独立迁移，此脚本仅验证 PC 端配置\n', 'yellow');

  const checks = [
    { name: 'PC端 vite.config.js', fn: checkPcViteConfig },
  ];

  let allPassed = true;
  const results = [];

  for (const check of checks) {
    log(`\n检查: ${check.name}`, 'blue');
    try {
      const result = check.fn();
      results.push({ name: check.name, passed: result });
      if (!result) {
        allPassed = false;
      }
    } catch (error) {
      log(`❌ 检查失败: ${error.message}`, 'red');
      results.push({ name: check.name, passed: false });
      allPassed = false;
    }
  }

  log('\n' + '='.repeat(50), 'blue');
  log('📊 验证结果汇总', 'blue');
  log('='.repeat(50) + '\n', 'blue');

  results.forEach(result => {
    const icon = result.passed ? '✅' : '❌';
    const color = result.passed ? 'green' : 'red';
    log(`${icon} ${result.name}`, color);
  });

  log('\n' + '='.repeat(50), 'blue');
  if (allPassed) {
    log('✅ 所有检查通过！路径配置正确。', 'green');
    process.exit(0);
  } else {
    log('❌ 部分检查未通过，请修复上述问题后重试。', 'red');
    process.exit(1);
  }
}

main();
