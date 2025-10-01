module.exports = {
    // User directory - this is where Node-RED will store flows and settings
    userDir: '/data',
    
    // Flow file location
    flowFile: 'flows.json',
    
    // Enable projects
    enableProjects: process.env.NODE_RED_ENABLE_PROJECTS === 'true',
    
    // HTTP settings
    httpNodeRoot: '/',
    httpAdminRoot: '/',
    
    // Logging
    logging: {
        console: {
            level: "info",
            metrics: false,
            audit: false
        }
    },
    
    // Editor settings
    editorTheme: {
        projects: {
            enabled: false
        }
    }
}; 