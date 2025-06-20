#!/usr/bin/env python3
"""
Test Script for Desktop Screensaver
Tests all major components of the application
"""

import sys
import time
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    try:
        from src.core.config_manager import ConfigManager
        print("✓ ConfigManager imported successfully")
        
        from src.core.screensaver_manager import ScreensaverManager
        print("✓ ScreensaverManager imported successfully")
        
        from src.core.system_tray import SystemTray
        print("✓ SystemTray imported successfully")
        
        from src.ui.screensaver_window import ScreensaverWindow
        print("✓ ScreensaverWindow imported successfully")
        
        from src.ui.settings_dialog import SettingsDialog
        print("✓ SettingsDialog imported successfully")
        
        from src.utils.weather import WeatherWidget
        print("✓ WeatherWidget imported successfully")
        
        from src.utils.logger import setup_logging
        print("✓ Logger utilities imported successfully")
        
        from src.utils.error_handler import ErrorHandler
        print("✓ ErrorHandler imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False

def test_config_manager():
    """Test configuration manager"""
    print("\nTesting ConfigManager...")
    
    try:
        from src.core.config_manager import ConfigManager
        
        # Create config manager
        config = ConfigManager()
        print("✓ ConfigManager created successfully")
        
        # Test getting/setting values
        config.set('test.value', 'test_value')
        value = config.get('test.value', 'default')
        assert value == 'test_value', f"Expected 'test_value', got '{value}'"
        print("✓ Configuration get/set works")
        
        # Test default values
        default_value = config.get('nonexistent.key', 'default')
        assert default_value == 'default', f"Expected 'default', got '{default_value}'"
        print("✓ Default values work")
        
        return True
        
    except Exception as e:
        print(f"✗ ConfigManager test failed: {e}")
        return False

def test_logger():
    """Test logging system"""
    print("\nTesting Logger...")
    
    try:
        from src.utils.logger import setup_logging, get_logger
        
        # Setup logging
        setup_logging(log_level="DEBUG")
        print("✓ Logging setup successful")
        
        # Test logger
        logger = get_logger(__name__)
        logger.info("Test log message")
        print("✓ Logger works")
        
        return True
        
    except Exception as e:
        print(f"✗ Logger test failed: {e}")
        return False

def test_error_handler():
    """Test error handling"""
    print("\nTesting ErrorHandler...")
    
    try:
        from src.utils.error_handler import ErrorHandler
        
        # Create error handler
        error_handler = ErrorHandler()
        print("✓ ErrorHandler created successfully")
        
        # Test error handling
        error_handler.handle_error("Test error message", show_dialog=False)
        print("✓ Error handling works")
        
        return True
        
    except Exception as e:
        print(f"✗ ErrorHandler test failed: {e}")
        return False

def test_weather_widget():
    """Test weather widget (without API calls)"""
    print("\nTesting WeatherWidget...")
    
    try:
        from src.core.config_manager import ConfigManager
        from src.ui.screensaver_window import ScreensaverWindow
        
        # Create config manager
        config = ConfigManager()
        
        # Test weather widget creation
        from src.utils.weather import WeatherWidget
        weather_widget = WeatherWidget(config)
        print("✓ WeatherWidget created successfully")
        
        # Test weather summary
        summary = weather_widget.get_weather_summary()
        assert isinstance(summary, str), f"Expected string, got {type(summary)}"
        print("✓ Weather summary works")
        
        return True
        
    except Exception as e:
        print(f"✗ WeatherWidget test failed: {e}")
        return False

def test_screensaver_window():
    """Test screensaver window creation"""
    print("\nTesting ScreensaverWindow...")
    
    try:
        from src.core.config_manager import ConfigManager
        from src.ui.screensaver_window import ScreensaverWindow
        
        # Create config manager
        config = ConfigManager()
        
        # Create screensaver window
        window = ScreensaverWindow(config)
        print("✓ ScreensaverWindow created successfully")
        
        # Test window properties
        assert window.isVisible() == False, "Window should not be visible initially"
        print("✓ Window properties correct")
        
        # Clean up
        window.close()
        
        return True
        
    except Exception as e:
        print(f"✗ ScreensaverWindow test failed: {e}")
        return False

def test_system_tray():
    """Test system tray creation"""
    print("\nTesting SystemTray...")
    
    try:
        from src.core.config_manager import ConfigManager
        from src.core.screensaver_manager import ScreensaverManager
        from src.core.system_tray import SystemTray
        
        # Create managers
        config = ConfigManager()
        screensaver_manager = ScreensaverManager(config)
        
        # Create system tray
        tray = SystemTray(screensaver_manager, config)
        print("✓ SystemTray created successfully")
        
        # Test tray properties
        assert hasattr(tray, 'tray_icon'), "Tray should have tray_icon"
        print("✓ Tray properties correct")
        
        return True
        
    except Exception as e:
        print(f"✗ SystemTray test failed: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("Desktop Screensaver - Component Tests")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_logger,
        test_error_handler,
        test_config_manager,
        test_weather_widget,
        test_screensaver_window,
        test_system_tray,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"✗ {test.__name__} failed")
        except Exception as e:
            print(f"✗ {test.__name__} crashed: {e}")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The application is ready to use.")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False

def main():
    """Main test function"""
    try:
        success = run_all_tests()
        
        if success:
            print("\nTo run the application:")
            print("python main.py")
        else:
            print("\nPlease fix the failing tests before running the application.")
            
    except KeyboardInterrupt:
        print("\nTests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error during testing: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 