#!/usr/bin/env node

/**
 * 自动修复所有路径配置脚本
 * 确保所有配置文件都包含正确的路径设置
 * 
 * 注意：移动端项目已独立迁移，此脚本仅处理 PC 端配置
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

function fixPcViteConfig() {
  const configPath = path.join(projectRoot, 'sau_frontend', 'vite.config.js');
  
  if (!fs.existsSync(configPath)) {
    log(`❌ PC端 vite.config.js 不存在: ${configPath}`, 'red');
    return false;
  }

  let content = fs.readFileSync(configPath, 'utf8');
  const original = content;

  // 检查是否已有 allowedHosts
  if (content.includes('allowedHosts')) {
    // 检查是否包含 yutt.xyz
    if (!content.includes("'yutt.xyz'") && !content.includes('"yutt.xyz"')) {
      // 更新 allowedHosts
      content = content.replace(
        /allowedHosts:\s*\[[^\]]*\]/,
        `allowedHosts: ['yutt.xyz']`
      );
    } else {
      log(`✅ PC端 vite.config.js allowedHosts 已配置`, 'green');
      return true;
    }
  } else {
    // 在 server 配置中添加 allowedHosts
    if (content.includes('server:')) {
      // 在 server 对象中添加 allowedHosts
      content = content.replace(
        /server:\s*\{/,
        `server: {\n    // 允许的主机名列表\n    allowedHosts: ['yutt.xyz'],`
      );
    } else {
      log(`⚠️  PC端 vite.config.js 缺少 server 配置，无法自动修复`, 'yellow');
      return false;
    }
  }

  if (content !== original) {
    fs.writeFileSync(configPath, content, 'utf8');
    log(`✅ 已修复 PC端 vite.config.js`, 'green');
    return true;
  }

  return true;
}

function main() {
  log('\n🔧 开始自动修复路径配置...\n', 'blue');
  log('注意：移动端项目已独立迁移，此脚本仅处理 PC 端配置\n', 'yellow');

  const fixes = [
    { name: 'PC端 vite.config.js', fn: fixPcViteConfig },
  ];

  let allFixed = true;

  for (const fix of fixes) {
    log(`\n修复: ${fix.name}`, 'blue');
    try {
      const result = fix.fn();
      if (!result) {
        allFixed = false;
      }
    } catch (error) {
      log(`❌ 修复失败: ${error.message}`, 'red');
      allFixed = false;
    }
  }

  log('\n' + '='.repeat(50), 'blue');
  if (allFixed) {
    log('✅ 所有配置已修复！', 'green');
  } else {
    log('⚠️  部分配置修复失败，请手动检查', 'yellow');
  }
  log('='.repeat(50) + '\n', 'blue');
}

main();
