/**
 * Network Visualization - D3.js visualization for career network analysis
 */

// Global variables to store the simulation and svg
let simulation;
let svg;
let width;
let height;
let nodeElements;
let linkElements;
let nodeInfoElement;

/**
 * Initialize the network visualization
 * @param {string} containerId - The ID of the container element
 * @param {string} nodeInfoId - The ID of the node info element
 * @param {Object} data - The network data object with nodes and links
 */
function initNetworkVisualization(containerId, nodeInfoId, data) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    nodeInfoElement = document.getElementById(nodeInfoId);
    
    // Set dimensions
    width = container.clientWidth;
    height = container.clientHeight;
    
    // Create SVG element
    svg = d3.select(`#${containerId}`)
        .append('svg')
        .attr('width', width)
        .attr('height', height)
        .call(d3.zoom().on('zoom', function(event) {
            svg.select('g').attr('transform', event.transform);
        }))
        .append('g');
    
    // Create the links
    linkElements = svg.append('g')
        .selectAll('line')
        .data(data.links)
        .enter()
        .append('line')
        .attr('stroke-width', d => d.value)
        .attr('stroke', 'rgba(255, 255, 255, 0.2)');
    
    // Create the nodes
    nodeElements = svg.append('g')
        .selectAll('circle')
        .data(data.nodes)
        .enter()
        .append('circle')
        .attr('r', d => d.size)
        .attr('fill', getNodeColor)
        .call(d3.drag()
            .on('start', dragStarted)
            .on('drag', dragging)
            .on('end', dragEnded))
        .on('mouseover', showNodeInfo)
        .on('mouseout', hideNodeInfo)
        .on('click', highlightConnections);
    
    // Add labels to nodes
    const textElements = svg.append('g')
        .selectAll('text')
        .data(data.nodes)
        .enter()
        .append('text')
        .text(d => d.name)
        .attr('font-size', 12)
        .attr('dx', 15)
        .attr('dy', 4)
        .attr('fill', 'rgba(255, 255, 255, 0.7)');
    
    // Create the simulation
    simulation = d3.forceSimulation()
        .nodes(data.nodes)
        .force('link', d3.forceLink()
            .id(d => d.id)
            .links(data.links)
            .distance(100)
            .strength(0.5))
        .force('charge', d3.forceManyBody().strength(-300))
        .force('center', d3.forceCenter(width / 2, height / 2))
        .force('collision', d3.forceCollide().radius(d => d.size + 10))
        .on('tick', ticked);
    
    // Tick function to update positions
    function ticked() {
        linkElements
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);
        
        nodeElements
            .attr('cx', d => d.x)
            .attr('cy', d => d.y);
        
        textElements
            .attr('x', d => d.x)
            .attr('y', d => d.y);
    }
    
    // Get color based on node group
    function getNodeColor(node) {
        switch(node.group) {
            case 1: return '#0d6efd'; // Primary path - blue
            case 2: return '#6c757d'; // Skills - gray
            case 3: return '#6f42c1'; // Alternative paths - purple
            default: return '#20c997'; // Default - teal
        }
    }
    
    // Show node info on hover
    function showNodeInfo(event, d) {
        // Position the info div near the mouse
        const [x, y] = d3.pointer(event, container);
        
        nodeInfoElement.style.left = `${x + 10}px`;
        nodeInfoElement.style.top = `${y + 10}px`;
        nodeInfoElement.style.display = 'block';
        
        // Set the content based on node type
        let content = `<h6>${d.name}</h6>`;
        
        switch(d.group) {
            case 1:
                content += '<p class="small mb-0 text-primary">Primary Career Path</p>';
                break;
            case 2:
                content += '<p class="small mb-0 text-secondary">Required Skill</p>';
                break;
            case 3:
                content += '<p class="small mb-0 text-purple">Alternative Career Path</p>';
                break;
        }
        
        nodeInfoElement.innerHTML = content;
    }
    
    // Hide node info when not hovering
    function hideNodeInfo() {
        nodeInfoElement.style.display = 'none';
    }
    
    // Highlight connections when a node is clicked
    function highlightConnections(event, d) {
        // Reset all nodes and links
        nodeElements.attr('opacity', 0.3);
        linkElements.attr('opacity', 0.1);
        
        // Highlight the clicked node
        d3.select(this).attr('opacity', 1);
        
        // Find connected nodes and links
        const connectedNodeIds = data.links
            .filter(link => link.source.id === d.id || link.target.id === d.id)
            .map(link => link.source.id === d.id ? link.target.id : link.source.id);
        
        // Highlight connected nodes
        nodeElements
            .filter(node => connectedNodeIds.includes(node.id))
            .attr('opacity', 1);
        
        // Highlight connected links
        linkElements
            .filter(link => link.source.id === d.id || link.target.id === d.id)
            .attr('opacity', 1)
            .attr('stroke', 'rgba(255, 255, 255, 0.6)');
        
        // Add a double-click listener to reset
        d3.select('svg').on('dblclick', resetHighlighting);
    }
    
    // Reset highlighting
    function resetHighlighting() {
        nodeElements.attr('opacity', 1);
        linkElements.attr('opacity', 1).attr('stroke', 'rgba(255, 255, 255, 0.2)');
    }
}

/**
 * Functions for handling node dragging
 */
function dragStarted(event, d) {
    if (!event.active) simulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
}

function dragging(event, d) {
    d.fx = event.x;
    d.fy = event.y;
}

function dragEnded(event, d) {
    if (!event.active) simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
}

/**
 * Change the layout of the network
 * @param {string} layout - The layout type: 'force', 'radial', or 'circle'
 */
function changeLayout(layout) {
    // Stop the current simulation
    simulation.stop();
    
    // Reset any fixed positions
    simulation.nodes().forEach(node => {
        node.fx = null;
        node.fy = null;
    });
    
    // Apply the new layout
    switch(layout) {
        case 'force':
            // Standard force-directed layout
            simulation
                .force('link', d3.forceLink()
                    .id(d => d.id)
                    .links(simulation.force('link').links())
                    .distance(100)
                    .strength(0.5))
                .force('charge', d3.forceManyBody().strength(-300))
                .force('center', d3.forceCenter(width / 2, height / 2))
                .force('x', null)
                .force('y', null);
            break;
            
        case 'radial':
            // Radial layout
            simulation
                .force('link', d3.forceLink()
                    .id(d => d.id)
                    .links(simulation.force('link').links())
                    .distance(100)
                    .strength(0.3))
                .force('charge', d3.forceManyBody().strength(-100))
                .force('center', null)
                .force('x', d3.forceX(width / 2).strength(0.1))
                .force('y', d3.forceY(height / 2).strength(0.1))
                .force('r', d3.forceRadial(function(d) {
                    // Different radii based on node group
                    return d.group === 1 ? 0 : 
                           d.group === 2 ? 150 : 
                           250;
                }, width / 2, height / 2).strength(1));
            break;
            
        case 'circle':
            // Circular layout
            simulation
                .force('link', d3.forceLink()
                    .id(d => d.id)
                    .links(simulation.force('link').links())
                    .distance(50)
                    .strength(0.2))
                .force('charge', d3.forceManyBody().strength(-50))
                .force('center', d3.forceCenter(width / 2, height / 2))
                .force('x', null)
                .force('y', null)
                .force('r', null)
                .force('circle', d3.forceX(function(d, i) {
                    const angle = (i / simulation.nodes().length) * Math.PI * 2;
                    return width / 2 + Math.cos(angle) * 200;
                }).strength(1))
                .force('circle-y', d3.forceY(function(d, i) {
                    const angle = (i / simulation.nodes().length) * Math.PI * 2;
                    return height / 2 + Math.sin(angle) * 200;
                }).strength(1));
            break;
    }
    
    // Restart the simulation
    simulation.alpha(1).restart();
}

/**
 * Update the link strength of the simulation
 * @param {number} strength - The link strength value (0-1)
 */
function updateLinkStrength(strength) {
    simulation.force('link').strength(strength);
    simulation.alpha(1).restart();
}

/**
 * Recenter the visualization
 */
function recenterVisualization() {
    // Reset any fixed positions
    simulation.nodes().forEach(node => {
        node.fx = null;
        node.fy = null;
    });
    
    // Reset the zoom
    svg.transition()
       .duration(750)
       .call(d3.zoom().transform, d3.zoomIdentity);
    
    // Re-center the nodes
    simulation
        .force('center', d3.forceCenter(width / 2, height / 2))
        .alpha(1)
        .restart();
}
