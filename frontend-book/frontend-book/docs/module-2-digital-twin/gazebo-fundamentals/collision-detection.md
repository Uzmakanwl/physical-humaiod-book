# Collision Detection in Gazebo

Collision detection is a critical component of physics simulation that determines how objects interact with each other and their environment. In humanoid robot simulation, accurate collision detection is essential for realistic behavior, safety validation, and proper interaction with the environment.

## Understanding Collision Detection

### Basic Concepts
Collision detection in Gazebo involves two main phases:
- **Broad Phase**: Quickly identifies potential collision pairs using spatial partitioning
- **Narrow Phase**: Performs precise collision detection on potential pairs

### Types of Collisions
- **Static Collisions**: Between objects and static environment
- **Dynamic Collisions**: Between moving objects
- **Self-Collisions**: Between different parts of the same robot (usually disabled for robots)

## Collision Detection Methods

### Contact Detection
Gazebo uses the Open Dynamics Engine (ODE), Bullet Physics, or Simbody for collision detection:

#### ODE (Open Dynamics Engine)
- Default physics engine in many Gazebo versions
- Good performance for most robotics applications
- Supports various primitive shapes and meshes

#### Bullet Physics
- More advanced collision detection capabilities
- Better handling of complex geometries
- Often preferred for complex humanoid robots

#### Simbody
- More accurate but computationally expensive
- Better for high-precision applications

## Collision Geometry Types

### Primitive Shapes
Simple geometric shapes that provide efficient collision detection:

#### Box
```xml
<collision name="box_collision">
  <geometry>
    <box>
      <size>1.0 2.0 0.5</size>
    </box>
  </geometry>
</collision>
```

#### Sphere
```xml
<collision name="sphere_collision">
  <geometry>
    <sphere>
      <radius>0.3</radius>
    </sphere>
  </geometry>
</collision>
```

#### Cylinder
```xml
<collision name="cylinder_collision">
  <geometry>
    <cylinder>
      <radius>0.2</radius>
      <length>0.5</length>
    </cylinder>
  </geometry>
</collision>
```

#### Capsule
```xml
<collision name="capsule_collision">
  <geometry>
    <capsule>
      <radius>0.1</radius>
      <length>0.3</length>
    </capsule>
  </geometry>
</collision>
```

### Mesh Collisions
For complex shapes, you can use mesh files:
```xml
<collision name="mesh_collision">
  <geometry>
    <mesh>
      <uri>file://meshes/complex_shape.dae</uri>
    </mesh>
  </geometry>
</collision>
```

### Heightmap Collisions
For terrain and complex surfaces:
```xml
<collision name="terrain_collision">
  <geometry>
    <heightmap>
      <uri>file://materials/textures/heightmap.png</uri>
      <size>10 10 2</size>
    </heightmap>
  </geometry>
</collision>
```

## Collision Properties

### Surface Properties
Define how objects behave when they collide:

#### Friction
```xml
<collision name="collision">
  <surface>
    <friction>
      <ode>
        <mu>1.0</mu>  <!-- Static friction coefficient -->
        <mu2>1.0</mu2>  <!-- Secondary friction coefficient -->
      </ode>
    </friction>
  </surface>
</collision>
```

#### Restitution (Bounciness)
```xml
<collision name="collision">
  <surface>
    <bounce>
      <restitution_coefficient>0.2</restitution_coefficient>
      <threshold>100000</threshold>
    </bounce>
  </surface>
</collision>
```

#### Contact Parameters
```xml
<collision name="collision">
  <surface>
    <contact>
      <ode>
        <soft_cfm>0</soft_cfm>
        <soft_erp>0.2</soft_erp>
        <kp>1e12</kp>  <!-- Contact stiffness -->
        <kd>1</kd>     <!-- Contact damping -->
        <max_vel>100.0</max_vel>
        <min_depth>0.001</min_depth>
      </ode>
    </contact>
  </surface>
</collision>
```

## Collision Detection in Humanoid Robots

### Self-Collision Avoidance
For humanoid robots, self-collision is typically disabled between adjacent links:
```xml
<link name="upper_arm">
  <collision name="upper_arm_collision">
    <geometry>
      <capsule>
        <radius>0.05</radius>
        <length>0.3</length>
      </capsule>
    </geometry>
  </collision>
  <!-- Self-collision is disabled by default for adjacent links -->
</link>
```

### End-Effector Considerations
For hands and feet, collision detection is critical:
- **Foot collisions**: Essential for balance and walking simulation
- **Hand collisions**: Important for manipulation tasks
- **Head collisions**: Important for safety in human environments

### Collision Filtering
Use collision groups and masks to control which objects can collide:
```xml
<collision name="collision">
  <surface>
    <contact>
      <collide_without_contact>0</collide_without_contact>
    </contact>
  </surface>
</collision>
```

## Collision Detection Performance

### Performance Factors
- **Complexity**: More complex geometries require more processing
- **Frequency**: Higher update rates require more processing power
- **Number of Objects**: More objects increase collision detection load

### Optimization Strategies
1. **Simplified Collision Models**: Use simpler geometries for collision than visual models
2. **Collision Level of Detail**: Use different collision models based on distance
3. **Spatial Partitioning**: Organize objects efficiently in space

### Simplified Collision Models
```xml
<!-- Visual model (complex) -->
<visual name="visual">
  <geometry>
    <mesh>
      <uri>file://meshes/complex_robot.dae</uri>
    </mesh>
  </geometry>
</visual>

<!-- Collision model (simplified) -->
<collision name="collision">
  <geometry>
    <box>
      <size>0.5 0.3 0.8</size>
    </box>
  </geometry>
</collision>
```

## Collision Detection in Simulation

### Contact Information
Gazebo provides detailed contact information:
- **Contact Points**: Where objects touch
- **Contact Forces**: Forces at contact points
- **Contact Normals**: Direction of contact forces

### Accessing Contact Information
Through ROS/Gazebo plugins, you can access contact data:
```cpp
// Example: Getting contact information
void ContactPlugin::OnContact(const ConstContactsPtr &_contacts) {
    for (int i = 0; i < _contacts->contact_size(); ++i) {
        std::string entity1 = _contacts->contact(i).collision1();
        std::string entity2 = _contacts->contact(i).collision2();

        for (int j = 0; j < _contacts->contact(i).position_size(); ++j) {
            ignition::math::Vector3d pos =
                msgs::Convert(_contacts->contact(i).position(j));
            ignition::math::Vector3d normal =
                msgs::Convert(_contacts->contact(i).normal(j));
            double depth = _contacts->contact(i).depth(j);
        }
    }
}
```

## Common Collision Issues and Solutions

### Penetration Problems
- **Issue**: Objects pass through each other
- **Solution**: Reduce time step, increase contact stiffness, or improve collision geometry

### Jittering/Stability
- **Issue**: Objects vibrate or jitter during contact
- **Solution**: Adjust ERP (Error Reduction Parameter) and CFM (Constraint Force Mixing)

### Performance Issues
- **Issue**: Slow simulation due to collision detection
- **Solution**: Simplify collision geometry, adjust physics parameters

### Tuning Parameters
```xml
<physics type="ode">
  <max_step_size>0.001</max_step_size>
  <real_time_factor>1</real_time_factor>
  <max_contacts>20</max_contacts>
  <gravity>0 0 -9.8</gravity>
  <ode>
    <solver>
      <type>quick</type>
      <iters>10</iters>
      <sor>1.3</sor>
    </solver>
    <constraints>
      <cfm>0</cfm>
      <erp>0.2</erp>
      <contact_max_correcting_vel>100</contact_max_correcting_vel>
      <contact_surface_layer>0.001</contact_surface_layer>
    </constraints>
  </ode>
</physics>
```

## Collision Detection for Safety

### Collision Avoidance
For humanoid robots operating near humans:
- **Safety Zones**: Define areas where collisions should be avoided
- **Emergency Stops**: Trigger when collisions exceed safe thresholds
- **Path Planning**: Use collision detection for safe navigation

### Impact Force Calculation
Understanding collision forces:
- **Force Magnitude**: How strong the collision is
- **Duration**: How long the collision lasts
- **Area**: Over what area the force is distributed

## Best Practices for Humanoid Robot Simulation

### Model Design
1. **Appropriate Collision Geometry**: Use shapes that approximate the actual geometry
2. **Conservative Approach**: When in doubt, use slightly larger collision shapes
3. **Layered Approach**: Use multiple collision elements for complex shapes

### Testing Strategies
1. **Edge Cases**: Test with extreme scenarios
2. **Performance Monitoring**: Monitor simulation performance
3. **Validation**: Compare simulation results with real-world data

### Safety Considerations
1. **Force Limits**: Define maximum acceptable collision forces
2. **Recovery Procedures**: Plan for collision scenarios
3. **Human Safety**: Ensure robot behavior is safe around humans

Collision detection forms the foundation for realistic interaction between humanoid robots and their environment. Properly configured collision detection ensures that robots behave realistically when interacting with objects and navigating through spaces.