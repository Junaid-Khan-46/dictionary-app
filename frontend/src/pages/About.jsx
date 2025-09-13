import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Code, Database, Shield, Zap, Users, Globe } from 'lucide-react';

const About = () => {
  const technologies = [
    {
      name: 'React',
      description: 'Modern frontend library with hooks and context',
      icon: <Code className="w-6 h-6" />,
      color: 'bg-blue-100 text-blue-600'
    },
    {
      name: 'FastAPI',
      description: 'High-performance Python web framework',
      icon: <Zap className="w-6 h-6" />,
      color: 'bg-green-100 text-green-600'
    },
    {
      name: 'MongoDB',
      description: 'NoSQL database for flexible data storage',
      icon: <Database className="w-6 h-6" />,
      color: 'bg-purple-100 text-purple-600'
    },
    {
      name: 'JWT Auth',
      description: 'Secure token-based authentication',
      icon: <Shield className="w-6 h-6" />,
      color: 'bg-red-100 text-red-600'
    },
    {
      name: 'TailwindCSS',
      description: 'Utility-first CSS framework',
      icon: <Globe className="w-6 h-6" />,
      color: 'bg-cyan-100 text-cyan-600'
    },
    {
      name: 'Vite',
      description: 'Fast build tool and development server',
      icon: <Users className="w-6 h-6" />,
      color: 'bg-yellow-100 text-yellow-600'
    }
  ];

  const features = [
    'User authentication and authorization',
    'Protected routes and role-based access',
    'CRUD operations with real-time updates',
    'Responsive design for all devices',
    'RESTful API with comprehensive documentation',
    'Environment-based configuration',
    'Production-ready deployment setup',
    'Modular and extensible architecture'
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <section className="bg-gradient-to-r from-indigo-600 to-blue-600 text-white">
        <div className="max-w-7xl mx-auto py-24 px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold mb-6">
              About Our Template
            </h1>
            <p className="text-xl md:text-2xl mb-8 text-indigo-100">
              A comprehensive full-stack solution for modern web development
            </p>
          </div>
        </div>
      </section>

      {/* Mission Section */}
      <section className="py-16">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-6">
              Our Mission
            </h2>
            <p className="text-lg text-gray-600 leading-relaxed">
              We believe that building modern web applications shouldn't be complicated. 
              Our full-stack template provides a solid foundation with industry best practices, 
              allowing developers to focus on building features rather than setting up infrastructure. 
              Whether you're a startup looking to prototype quickly or an enterprise team 
              building production applications, our template scales with your needs.
            </p>
          </div>
        </div>
      </section>

      {/* Technologies Section */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Built with Modern Technologies
            </h2>
            <p className="text-lg text-gray-600">
              Carefully selected tools and frameworks for optimal performance
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {technologies.map((tech, index) => (
              <Card key={index} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className={`w-12 h-12 rounded-lg ${tech.color} flex items-center justify-center mb-4`}>
                    {tech.icon}
                  </div>
                  <CardTitle>{tech.name}</CardTitle>
                  <CardDescription>{tech.description}</CardDescription>
                </CardHeader>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              What's Included
            </h2>
            <p className="text-lg text-gray-600">
              Everything you need to build and deploy modern web applications
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {features.map((feature, index) => (
              <div key={index} className="flex items-center space-x-3">
                <div className="flex-shrink-0">
                  <div className="w-6 h-6 bg-green-100 rounded-full flex items-center justify-center">
                    <div className="w-2 h-2 bg-green-600 rounded-full"></div>
                  </div>
                </div>
                <span className="text-gray-700">{feature}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-gray-900 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-4xl font-bold mb-2">100%</div>
              <div className="text-gray-300">Open Source</div>
            </div>
            <div>
              <div className="text-4xl font-bold mb-2">50+</div>
              <div className="text-gray-300">Components</div>
            </div>
            <div>
              <div className="text-4xl font-bold mb-2">24/7</div>
              <div className="text-gray-300">Community Support</div>
            </div>
            <div>
              <div className="text-4xl font-bold mb-2">∞</div>
              <div className="text-gray-300">Possibilities</div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default About;

