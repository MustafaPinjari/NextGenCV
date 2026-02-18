/**
 * Performance Monitoring Module
 * Tracks Core Web Vitals, page load times, and animation frame rates
 * 
 * Requirements: 14.6
 */

(function() {
    'use strict';

    // ============================================================================
    // Configuration
    // ============================================================================

    const config = {
        // Enable/disable monitoring
        enabled: true,
        
        // Send metrics to server
        reportToServer: true,
        reportEndpoint: '/api/performance/metrics/',
        
        // Console logging
        logToConsole: true,
        
        // Thresholds for warnings
        thresholds: {
            FCP: 1800,  // First Contentful Paint (ms)
            LCP: 2500,  // Largest Contentful Paint (ms)
            FID: 100,   // First Input Delay (ms)
            CLS: 0.1,   // Cumulative Layout Shift
            TTFB: 600,  // Time to First Byte (ms)
            FPS: 50     // Frames per second (minimum)
        }
    };

    // ============================================================================
    // Core Web Vitals Tracking
    // ============================================================================

    const metrics = {
        FCP: null,  // First Contentful Paint
        LCP: null,  // Largest Contentful Paint
        FID: null,  // First Input Delay
        CLS: 0,     // Cumulative Layout Shift
        TTFB: null, // Time to First Byte
        FPS: [],    // Frame rates
        pageLoadTime: null,
        domContentLoadedTime: null,
        resourceLoadTime: null
    };

    /**
     * Track First Contentful Paint (FCP)
     */
    function trackFCP() {
        if (!window.PerformanceObserver) return;

        try {
            const observer = new PerformanceObserver((list) => {
                for (const entry of list.getEntries()) {
                    if (entry.name === 'first-contentful-paint') {
                        metrics.FCP = entry.startTime;
                        logMetric('FCP', metrics.FCP, config.thresholds.FCP);
                        observer.disconnect();
                    }
                }
            });

            observer.observe({ entryTypes: ['paint'] });
        } catch (e) {
            console.error('Error tracking FCP:', e);
        }
    }

    /**
     * Track Largest Contentful Paint (LCP)
     */
    function trackLCP() {
        if (!window.PerformanceObserver) return;

        try {
            const observer = new PerformanceObserver((list) => {
                const entries = list.getEntries();
                const lastEntry = entries[entries.length - 1];
                metrics.LCP = lastEntry.renderTime || lastEntry.loadTime;
                logMetric('LCP', metrics.LCP, config.thresholds.LCP);
            });

            observer.observe({ entryTypes: ['largest-contentful-paint'] });
        } catch (e) {
            console.error('Error tracking LCP:', e);
        }
    }

    /**
     * Track First Input Delay (FID)
     */
    function trackFID() {
        if (!window.PerformanceObserver) return;

        try {
            const observer = new PerformanceObserver((list) => {
                for (const entry of list.getEntries()) {
                    metrics.FID = entry.processingStart - entry.startTime;
                    logMetric('FID', metrics.FID, config.thresholds.FID);
                    observer.disconnect();
                }
            });

            observer.observe({ entryTypes: ['first-input'] });
        } catch (e) {
            console.error('Error tracking FID:', e);
        }
    }

    /**
     * Track Cumulative Layout Shift (CLS)
     */
    function trackCLS() {
        if (!window.PerformanceObserver) return;

        try {
            let clsValue = 0;
            const observer = new PerformanceObserver((list) => {
                for (const entry of list.getEntries()) {
                    if (!entry.hadRecentInput) {
                        clsValue += entry.value;
                        metrics.CLS = clsValue;
                    }
                }
                logMetric('CLS', metrics.CLS, config.thresholds.CLS);
            });

            observer.observe({ entryTypes: ['layout-shift'] });
        } catch (e) {
            console.error('Error tracking CLS:', e);
        }
    }

    /**
     * Track Time to First Byte (TTFB)
     */
    function trackTTFB() {
        if (!window.performance || !window.performance.timing) return;

        try {
            window.addEventListener('load', () => {
                const timing = performance.timing;
                metrics.TTFB = timing.responseStart - timing.requestStart;
                logMetric('TTFB', metrics.TTFB, config.thresholds.TTFB);
            });
        } catch (e) {
            console.error('Error tracking TTFB:', e);
        }
    }

    // ============================================================================
    // Page Load Time Tracking
    // ============================================================================

    /**
     * Track page load times
     */
    function trackPageLoadTimes() {
        if (!window.performance || !window.performance.timing) return;

        window.addEventListener('load', () => {
            const timing = performance.timing;
            
            // Page load time
            metrics.pageLoadTime = timing.loadEventEnd - timing.navigationStart;
            
            // DOM content loaded time
            metrics.domContentLoadedTime = timing.domContentLoadedEventEnd - timing.navigationStart;
            
            // Resource load time
            metrics.resourceLoadTime = timing.loadEventEnd - timing.domContentLoadedEventEnd;

            logMetric('Page Load Time', metrics.pageLoadTime);
            logMetric('DOM Content Loaded', metrics.domContentLoadedTime);
            logMetric('Resource Load Time', metrics.resourceLoadTime);

            // Report all metrics after page load
            setTimeout(reportMetrics, 1000);
        });
    }

    // ============================================================================
    // Animation Frame Rate Monitoring
    // ============================================================================

    let frameCount = 0;
    let lastFrameTime = performance.now();
    let fpsCheckInterval = null;

    /**
     * Monitor animation frame rates
     */
    function trackFPS() {
        function measureFrame() {
            const now = performance.now();
            const delta = now - lastFrameTime;
            
            if (delta > 0) {
                const fps = 1000 / delta;
                frameCount++;
                
                // Store FPS sample
                if (frameCount % 60 === 0) {  // Sample every 60 frames
                    metrics.FPS.push(fps);
                    
                    // Keep only last 100 samples
                    if (metrics.FPS.length > 100) {
                        metrics.FPS.shift();
                    }
                }
            }
            
            lastFrameTime = now;
            requestAnimationFrame(measureFrame);
        }

        requestAnimationFrame(measureFrame);

        // Check average FPS every 5 seconds
        fpsCheckInterval = setInterval(() => {
            if (metrics.FPS.length > 0) {
                const avgFPS = metrics.FPS.reduce((a, b) => a + b, 0) / metrics.FPS.length;
                logMetric('Average FPS', avgFPS.toFixed(2), config.thresholds.FPS);
                
                if (avgFPS < config.thresholds.FPS) {
                    console.warn(`⚠️ Low frame rate detected: ${avgFPS.toFixed(2)} FPS`);
                }
            }
        }, 5000);
    }

    /**
     * Stop FPS monitoring
     */
    function stopFPSTracking() {
        if (fpsCheckInterval) {
            clearInterval(fpsCheckInterval);
            fpsCheckInterval = null;
        }
    }

    // ============================================================================
    // Resource Timing
    // ============================================================================

    /**
     * Track resource loading performance
     */
    function trackResourceTiming() {
        if (!window.performance || !window.performance.getEntriesByType) return;

        window.addEventListener('load', () => {
            const resources = performance.getEntriesByType('resource');
            
            const resourceStats = {
                total: resources.length,
                css: 0,
                js: 0,
                images: 0,
                fonts: 0,
                other: 0,
                totalSize: 0,
                totalDuration: 0
            };

            resources.forEach(resource => {
                // Count by type
                if (resource.name.endsWith('.css')) {
                    resourceStats.css++;
                } else if (resource.name.endsWith('.js')) {
                    resourceStats.js++;
                } else if (resource.name.match(/\.(jpg|jpeg|png|gif|svg|webp)$/i)) {
                    resourceStats.images++;
                } else if (resource.name.match(/\.(woff|woff2|ttf|otf)$/i)) {
                    resourceStats.fonts++;
                } else {
                    resourceStats.other++;
                }

                // Sum size and duration
                resourceStats.totalSize += resource.transferSize || 0;
                resourceStats.totalDuration += resource.duration || 0;
            });

            if (config.logToConsole) {
                console.log('📊 Resource Loading Stats:', resourceStats);
            }

            // Find slow resources
            const slowResources = resources.filter(r => r.duration > 1000);
            if (slowResources.length > 0) {
                console.warn('⚠️ Slow resources detected:', slowResources.map(r => ({
                    name: r.name,
                    duration: r.duration.toFixed(2) + 'ms'
                })));
            }
        });
    }

    // ============================================================================
    // Long Tasks Detection
    // ============================================================================

    /**
     * Detect long tasks that block the main thread
     */
    function trackLongTasks() {
        if (!window.PerformanceObserver) return;

        try {
            const observer = new PerformanceObserver((list) => {
                for (const entry of list.getEntries()) {
                    console.warn('⚠️ Long task detected:', {
                        duration: entry.duration.toFixed(2) + 'ms',
                        startTime: entry.startTime.toFixed(2) + 'ms'
                    });
                }
            });

            observer.observe({ entryTypes: ['longtask'] });
        } catch (e) {
            // Long task API not supported
        }
    }

    // ============================================================================
    // Logging and Reporting
    // ============================================================================

    /**
     * Log metric to console
     */
    function logMetric(name, value, threshold) {
        if (!config.logToConsole) return;

        const formattedValue = typeof value === 'number' ? value.toFixed(2) : value;
        const unit = name.includes('FPS') ? ' FPS' : ' ms';
        
        let status = '✓';
        let style = 'color: green';
        
        if (threshold && value > threshold) {
            status = '⚠️';
            style = 'color: orange';
        }

        console.log(`%c${status} ${name}: ${formattedValue}${unit}`, style);
    }

    /**
     * Report metrics to server
     */
    function reportMetrics() {
        if (!config.reportToServer) return;

        const data = {
            url: window.location.href,
            userAgent: navigator.userAgent,
            timestamp: new Date().toISOString(),
            metrics: {
                FCP: metrics.FCP,
                LCP: metrics.LCP,
                FID: metrics.FID,
                CLS: metrics.CLS,
                TTFB: metrics.TTFB,
                pageLoadTime: metrics.pageLoadTime,
                domContentLoadedTime: metrics.domContentLoadedTime,
                resourceLoadTime: metrics.resourceLoadTime,
                avgFPS: metrics.FPS.length > 0 
                    ? metrics.FPS.reduce((a, b) => a + b, 0) / metrics.FPS.length 
                    : null
            }
        };

        // Send to server (if endpoint exists)
        if (config.reportEndpoint) {
            fetch(config.reportEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            }).catch(err => {
                // Silently fail if endpoint doesn't exist
                console.debug('Performance metrics not sent:', err.message);
            });
        }
    }

    /**
     * Get current metrics
     */
    function getMetrics() {
        return {
            ...metrics,
            avgFPS: metrics.FPS.length > 0 
                ? metrics.FPS.reduce((a, b) => a + b, 0) / metrics.FPS.length 
                : null
        };
    }

    /**
     * Print performance report to console
     */
    function printReport() {
        console.log('═══════════════════════════════════════════════════════');
        console.log('📊 Performance Report');
        console.log('═══════════════════════════════════════════════════════');
        console.log('');
        console.log('Core Web Vitals:');
        logMetric('  FCP', metrics.FCP, config.thresholds.FCP);
        logMetric('  LCP', metrics.LCP, config.thresholds.LCP);
        logMetric('  FID', metrics.FID, config.thresholds.FID);
        logMetric('  CLS', metrics.CLS, config.thresholds.CLS);
        console.log('');
        console.log('Page Load Times:');
        logMetric('  TTFB', metrics.TTFB, config.thresholds.TTFB);
        logMetric('  DOM Content Loaded', metrics.domContentLoadedTime);
        logMetric('  Page Load', metrics.pageLoadTime);
        logMetric('  Resource Load', metrics.resourceLoadTime);
        console.log('');
        console.log('Animation Performance:');
        if (metrics.FPS.length > 0) {
            const avgFPS = metrics.FPS.reduce((a, b) => a + b, 0) / metrics.FPS.length;
            logMetric('  Average FPS', avgFPS, config.thresholds.FPS);
        }
        console.log('');
        console.log('═══════════════════════════════════════════════════════');
    }

    // ============================================================================
    // Initialization
    // ============================================================================

    /**
     * Initialize performance monitoring
     */
    function init() {
        if (!config.enabled) return;

        console.log('🚀 Performance monitoring initialized');

        // Track Core Web Vitals
        trackFCP();
        trackLCP();
        trackFID();
        trackCLS();
        trackTTFB();

        // Track page load times
        trackPageLoadTimes();

        // Track resource timing
        trackResourceTiming();

        // Track long tasks
        trackLongTasks();

        // Track FPS (only if animations are present)
        if (document.querySelector('[class*="animate"], [class*="transition"]')) {
            trackFPS();
        }

        // Print report after page is fully loaded
        window.addEventListener('load', () => {
            setTimeout(printReport, 2000);
        });

        // Stop FPS tracking when page is hidden
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                stopFPSTracking();
            } else {
                trackFPS();
            }
        });
    }

    // Auto-initialize
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Export API
    window.PerformanceMonitor = {
        init,
        getMetrics,
        printReport,
        trackFPS,
        stopFPSTracking,
        config
    };

})();
