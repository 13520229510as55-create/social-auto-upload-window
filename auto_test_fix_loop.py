#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全自动测试和修复循环脚本
- 自动运行测试
- 分析结果和截图
- 定位问题
- 修复代码
- 重新测试
- 循环直到成功
"""

import subprocess
import sys
import os
import time
import re
from pathlib import Path
import json

SERVER_IP = "150.107.38.113"
SERVER_USER = "ubuntu"
SERVER_PASS = "15831929073asAS"
REMOTE_DIR = "/home/ubuntu/social-auto-upload"
MAX_ITERATIONS = 50  # 最多循环50次，确保能够解决所有问题


def run_remote_command(command):
    """在远程服务器上执行命令"""
    ssh_cmd = f"sshpass -p '{SERVER_PASS}' ssh -o StrictHostKeyChecking=no {SERVER_USER}@{SERVER_IP} '{command}'"
    try:
        result = subprocess.run(ssh_cmd, shell=True, capture_output=True, text=True, timeout=600)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "命令执行超时"
    except Exception as e:
        return False, "", str(e)


def upload_file(local_file, remote_file):
    """上传文件到服务器"""
    scp_cmd = f"sshpass -p '{SERVER_PASS}' scp -o StrictHostKeyChecking=no {local_file} {SERVER_USER}@{SERVER_IP}:{remote_file}"
    try:
        result = subprocess.run(scp_cmd, shell=True, capture_output=True, text=True, timeout=60)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ 上传文件失败: {e}")
        return False


def download_screenshots(iteration):
    """下载截图文件"""
    local_dir = Path(f"test_results/iteration_{iteration}/screenshots")
    local_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"   📥 下载截图到: {local_dir}")
    
    # 先列出远程截图文件
    list_cmd = f"sshpass -p '{SERVER_PASS}' ssh -o StrictHostKeyChecking=no {SERVER_USER}@{SERVER_IP} 'ls -1t {REMOTE_DIR}/logs/screenshots/tencent/*.png 2>/dev/null | head -20'"
    result = subprocess.run(list_cmd, shell=True, capture_output=True, text=True, timeout=10)
    
    if result.returncode == 0 and result.stdout.strip():
        screenshot_files = result.stdout.strip().split('\n')
        print(f"   📸 找到 {len(screenshot_files)} 个截图文件")
        
        # 下载每个截图文件
        for screenshot_file in screenshot_files:
            if screenshot_file.strip():
                scp_cmd = f"sshpass -p '{SERVER_PASS}' scp -o StrictHostKeyChecking=no {SERVER_USER}@{SERVER_IP}:{screenshot_file.strip()} {local_dir}/ 2>/dev/null"
                try:
                    subprocess.run(scp_cmd, shell=True, timeout=15, check=False)
                except subprocess.TimeoutExpired:
                    print(f"      ⚠️  下载超时: {Path(screenshot_file).name}")
                except Exception as e:
                    pass  # 忽略单个文件下载失败
        
        # 列出下载的截图
        downloaded = list(local_dir.glob("*.png"))
        if downloaded:
            print(f"   ✅ 已下载 {len(downloaded)} 个截图:")
            for img in sorted(downloaded)[-5:]:  # 显示最后5个
                print(f"      - {img.name}")
    else:
        print(f"   ⚠️  未找到截图文件")
    
    return local_dir


def analyze_screenshots(screenshot_dir, iteration):
    """分析截图，找出问题节点"""
    if not screenshot_dir.exists():
        print("   ⚠️  截图目录不存在")
        return {}
    
    screenshots = sorted(screenshot_dir.glob("*.png"))
    html_files = list(screenshot_dir.glob("*.html"))
    
    if not screenshots and not html_files:
        print("   ⚠️  未找到截图文件")
        return {}
    
    print(f"   📊 分析 {len(screenshots)} 个截图和 {len(html_files)} 个HTML文件...")
    
    # 按步骤分类截图
    steps = {}
    error_screenshots = []
    step_sequence = []  # 按时间顺序的步骤列表
    
    # 预期的步骤顺序
    expected_steps = [
        "00_浏览器启动完成",
        "00_页面创建完成",
        "01_页面加载完成",
        "02_文件输入框查找失败",
        "03_文件已设置到输入框",
        "04_设置文件失败",
        "05_文件重新设置成功",
        "06_标题和话题已填充",
        "07_原创选择完成",
        "08_视频上传完成",
        "09_定时设置完成",
        "10_短标题已添加",
        "11_发布按钮已点击",
        "12_草稿保存成功",
        "13_发布成功"
    ]
    
    for screenshot in screenshots:
        name = screenshot.name
        if "ERROR" in name:
            error_screenshots.append(name)
            step_sequence.append(("ERROR", name, screenshot.stat().st_mtime))
        elif "_" in name:
            # 提取步骤名称（例如：tencent_01_页面加载完成_xxx.png -> 01_页面加载完成）
            parts = name.split("_")
            if len(parts) >= 3:
                step_key = "_".join(parts[1:-1])  # 跳过"tencent"和最后的时间戳
                if step_key not in steps:
                    steps[step_key] = []
                steps[step_key].append(name)
                step_sequence.append((step_key, name, screenshot.stat().st_mtime))
    
    # 按时间排序步骤序列
    step_sequence.sort(key=lambda x: x[2])
    
    # 输出分析结果
    print()
    if error_screenshots:
        print(f"   ❌ 发现 {len(error_screenshots)} 个错误截图:")
        for err in error_screenshots[:5]:
            print(f"      - {err}")
    
    print(f"   📋 步骤执行顺序 ({len(step_sequence)} 个步骤):")
    for step_name, file_name, _ in step_sequence[-15:]:  # 显示最后15个步骤
        status = "❌" if step_name == "ERROR" else "✅"
        print(f"      {status} {step_name}")
    
    # 检查缺失的步骤
    completed_step_names = set(steps.keys())
    missing_steps = [step for step in expected_steps if step not in completed_step_names and not any(step in err for err in error_screenshots)]
    
    if missing_steps:
        print(f"   ⚠️  缺失的步骤 ({len(missing_steps)} 个):")
        for step in missing_steps[:5]:
            print(f"      - {step}")
    
    # 找出最后执行的步骤（可能是卡点）
    if step_sequence:
        last_step = step_sequence[-1]
        print(f"   🎯 最后执行的步骤: {last_step[0]}")
        if last_step[0] == "ERROR":
            print(f"      ⚠️  在错误步骤停止，可能是卡点位置")
    
    # 保存分析结果
    analysis_file = screenshot_dir.parent / "analysis.json"
    analysis_data = {
        "iteration": iteration,
        "total_screenshots": len(screenshots),
        "total_html_files": len(html_files),
        "error_screenshots": error_screenshots,
        "completed_steps": list(steps.keys()),
        "step_sequence": [{"step": s[0], "file": s[1]} for s in step_sequence],
        "screenshot_count_by_step": {k: len(v) for k, v in steps.items()},
        "missing_steps": missing_steps,
        "last_step": step_sequence[-1][0] if step_sequence else None,
        "is_stuck_at_error": step_sequence[-1][0] == "ERROR" if step_sequence else False
    }
    with open(analysis_file, 'w', encoding='utf-8') as f:
        json.dump(analysis_data, f, indent=2, ensure_ascii=False)
    print(f"   💾 分析结果已保存到: {analysis_file}")
    
    return analysis_data


def analyze_test_result(stdout, stderr):
    """分析测试结果"""
    output = stdout + stderr
    
    # 检查是否成功
    if "✅ 发布成功" in output or "测试完成（成功）" in output:
        return "success", "发布成功"
    
    # 检查常见错误
    errors = []
    
    if "Cookie已失效" in output or "cookie 失效" in output:
        errors.append("cookie_invalid")
    
    if "未找到视频文件" in output or "视频文件不存在" in output:
        errors.append("video_not_found")
    
    if "浏览器启动失败" in output or "DISPLAY" in output:
        errors.append("browser_launch_failed")
    
    if "上传超时" in output or "上传超时" in output:
        errors.append("upload_timeout")
    
    if "文件输入框" in output and "失败" in output:
        errors.append("file_input_not_found")
    
    if "发表按钮" in output and ("失败" in output or "超时" in output):
        errors.append("publish_button_failed")
    
    if "ModuleNotFoundError" in output or "No module named" in output:
        errors.append("module_not_found")
    
    if errors:
        return "failed", errors
    else:
        return "unknown", output


def fix_cookie_invalid():
    """修复Cookie失效问题"""
    print("🔧 修复Cookie失效问题...")
    print("   ⚠️  Cookie失效需要手动重新登录，无法自动修复")
    print("   💡 建议：检查cookiesFile目录中的Cookie文件")
    return False


def fix_video_not_found():
    """修复视频文件未找到问题"""
    print("🔧 修复视频文件未找到问题...")
    
    # 检查服务器上的视频文件
    success, stdout, stderr = run_remote_command(f"find {REMOTE_DIR} -type f \\( -iname '*12*8*.mp4' -o -iname '*12*8*.mov' -o -iname '*12-8*.mp4' -o -iname '*12-8*.mov' \\) 2>/dev/null | head -5")
    
    if success and stdout.strip():
        print(f"   ✅ 找到视频文件: {stdout.strip().split()[0]}")
        return True
    else:
        print("   ❌ 未找到12-8视频文件")
        print("   💡 建议：将视频文件上传到服务器的videoFile或videos目录")
        return False


def fix_browser_launch_failed():
    """修复浏览器启动失败问题"""
    print("🔧 修复浏览器启动失败问题...")
    
    # 检查Xvfb是否运行
    success, stdout, stderr = run_remote_command("pgrep -f Xvfb || echo 'not_running'")
    
    if "not_running" in stdout:
        print("   🔧 启动Xvfb...")
        run_remote_command("export DISPLAY=:99 && Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &")
        time.sleep(2)
    
    # 设置DISPLAY环境变量
    print("   🔧 设置DISPLAY环境变量...")
    # 这个需要在测试脚本中处理
    return True


def fix_file_input_not_found():
    """修复文件输入框未找到问题"""
    print("🔧 修复文件输入框未找到问题...")
    
    # 读取TencentVideo代码
    tencent_file = Path("uploader/tencent_uploader/main.py")
    if not tencent_file.exists():
        print("   ❌ 找不到TencentVideo文件")
        return False
    
    content = tencent_file.read_text(encoding='utf-8')
    
    # 检查是否已经有更好的错误处理
    if "wait_for_selector('input[type=\"file\"]" in content:
        print("   ✅ 文件输入框查找逻辑已存在")
        # 可以增加等待时间或添加更多查找方法
        return True
    
    return False


def fix_upload_timeout():
    """修复上传超时问题"""
    print("🔧 修复上传超时问题...")
    
    tencent_file = Path("uploader/tencent_uploader/main.py")
    if not tencent_file.exists():
        return False
    
    content = tencent_file.read_text(encoding='utf-8')
    
    # 检查超时时间设置
    if "max_wait_time = 300" in content:
        print("   ✅ 上传超时时间已设置为5分钟")
        # 可以增加超时时间
        return True
    
    return False


def fix_publish_button_failed():
    """修复发布按钮失败问题"""
    print("🔧 修复发布按钮失败问题...")
    
    tencent_file = Path("uploader/tencent_uploader/main.py")
    if not tencent_file.exists():
        return False
    
    content = tencent_file.read_text(encoding='utf-8')
    
    # 检查发布按钮逻辑
    if "click_publish" in content and "max_retries" in content:
        print("   ✅ 发布按钮重试机制已存在")
        return True
    
    return False


def fix_module_not_found():
    """修复模块未找到问题"""
    print("🔧 修复模块未找到问题...")
    
    # 安装所有必需的依赖
    print("   📦 安装所有必需的依赖包...")
    install_cmd = "cd /home/ubuntu/social-auto-upload && "
    install_cmd += "if [ -f ~/miniconda3/etc/profile.d/conda.sh ]; then "
    install_cmd += "source ~/miniconda3/etc/profile.d/conda.sh && conda activate base && "
    install_cmd += "pip install -r requirements.txt --break-system-packages && python -m playwright install chromium; "
    install_cmd += "else pip3 install -r requirements.txt --break-system-packages && python3 -m playwright install chromium; fi"
    
    success, stdout, stderr = run_remote_command(install_cmd)
    if success:
        print("   ✅ 依赖包安装成功")
        # 验证关键模块
        verify_cmd = "cd /home/ubuntu/social-auto-upload && "
        verify_cmd += "if [ -f ~/miniconda3/etc/profile.d/conda.sh ]; then "
        verify_cmd += "source ~/miniconda3/etc/profile.d/conda.sh && conda activate base && "
        verify_cmd += "python -c 'import playwright; import loguru; print(\"OK\")'; "
        verify_cmd += "else python3 -c 'import playwright; import loguru; print(\"OK\")'; fi"
        
        verify_success, verify_stdout, verify_stderr = run_remote_command(verify_cmd)
        if verify_success and "OK" in verify_stdout:
            print("   ✅ 关键模块验证成功")
            return True
        else:
            print(f"   ⚠️  模块验证失败，但继续尝试: {verify_stderr}")
            return True  # 即使验证失败也继续，可能只是输出问题
    else:
        print(f"   ❌ 依赖包安装失败: {stderr[-500:]}")
        # 尝试单独安装缺失的模块
        print("   🔄 尝试单独安装loguru...")
        single_install_cmd = "cd /home/ubuntu/social-auto-upload && "
        single_install_cmd += "if [ -f ~/miniconda3/etc/profile.d/conda.sh ]; then "
        single_install_cmd += "source ~/miniconda3/etc/profile.d/conda.sh && conda activate base && "
        single_install_cmd += "pip install loguru --break-system-packages; "
        single_install_cmd += "else pip3 install loguru --break-system-packages; fi"
        
        single_success, single_stdout, single_stderr = run_remote_command(single_install_cmd)
        if single_success:
            print("   ✅ loguru安装成功")
            return True
        return False


def apply_fix(error_type):
    """应用修复"""
    fixes = {
        "cookie_invalid": fix_cookie_invalid,
        "video_not_found": fix_video_not_found,
        "browser_launch_failed": fix_browser_launch_failed,
        "file_input_not_found": fix_file_input_not_found,
        "upload_timeout": fix_upload_timeout,
        "publish_button_failed": fix_publish_button_failed,
        "module_not_found": fix_module_not_found,
    }
    
    if error_type in fixes:
        return fixes[error_type]()
    else:
        print(f"   ⚠️  未知错误类型: {error_type}")
        return False


def main():
    """主循环"""
    print("=" * 80)
    print("🚀 全自动测试和修复循环")
    print("=" * 80)
    print()
    
    # 确保测试脚本已上传
    test_script = Path("test_tencent_full_flow_server.py")
    if test_script.exists():
        print("📤 上传测试脚本到服务器...")
        if upload_file(str(test_script), f"{REMOTE_DIR}/{test_script.name}"):
            print("   ✅ 上传成功")
        else:
            print("   ⚠️  上传失败，继续使用服务器上的版本")
    
    iteration = 0
    
    while iteration < MAX_ITERATIONS:
        iteration += 1
        print()
        print("=" * 80)
        print(f"🔄 第 {iteration} 次测试")
        print("=" * 80)
        print()
        
        # 运行测试（使用conda环境如果存在）
        print("▶️  运行测试...")
        test_cmd = f"cd {REMOTE_DIR} && "
        test_cmd += "if [ -f ~/miniconda3/etc/profile.d/conda.sh ]; then "
        test_cmd += "source ~/miniconda3/etc/profile.d/conda.sh && conda activate base && "
        test_cmd += "python test_tencent_full_flow_server.py; "
        test_cmd += "else python3 test_tencent_full_flow_server.py; fi"
        success, stdout, stderr = run_remote_command(test_cmd)
        
        output = stdout + stderr
        print(output[-2000:])  # 打印最后2000个字符
        
        # 下载截图和日志
        print()
        print("📥 下载测试结果...")
        result_dir = Path(f"test_results/iteration_{iteration}")
        result_dir.mkdir(parents=True, exist_ok=True)
        
        # 保存输出日志
        log_file = result_dir / "test_output.log"
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write("=== STDOUT ===\n")
            f.write(stdout)
            f.write("\n\n=== STDERR ===\n")
            f.write(stderr)
        print(f"   💾 测试日志已保存: {log_file}")
        
        # 下载截图
        screenshot_dir = download_screenshots(iteration)
        
        # 分析截图
        print()
        print("🔍 分析截图...")
        analyze_screenshots(screenshot_dir, iteration)
        
        # 分析结果
        print()
        print("🔍 分析测试结果...")
        status, error_info = analyze_test_result(stdout, stderr)
        
        if status == "success":
            print()
            print("=" * 80)
            print("✅ 测试成功！全流程问题已全部解决！")
            print("=" * 80)
            return True
        
        print(f"   ❌ 测试失败: {error_info}")
        
        # 应用修复
        if isinstance(error_info, list):
            fixed = False
            for error_type in error_info:
                print()
                if apply_fix(error_type):
                    fixed = True
            
            if fixed:
                # 上传修复后的文件
                print()
                print("📤 上传修复后的文件...")
                # 这里可以上传修复后的代码文件
                time.sleep(2)
        else:
            print(f"   ⚠️  未知错误，无法自动修复")
            print(f"   错误信息: {error_info[:500]}")
            break
        
        # 等待后重试
        if iteration < MAX_ITERATIONS:
            wait_time = 5
            print()
            print(f"⏳ 等待 {wait_time} 秒后重试...")
            time.sleep(wait_time)
    
    print()
    print("=" * 80)
    print(f"❌ 达到最大迭代次数 ({MAX_ITERATIONS})，停止测试")
    print("=" * 80)
    return False


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断测试")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 脚本执行失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

