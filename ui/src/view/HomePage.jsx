import { motion } from "framer-motion";

const FeatureCard = ({ title, description, animationDelay }) => (
  <motion.div
    className="bg-gray-900/50 p-6 rounded-lg border border-white/10"
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.5, delay: animationDelay }}
  >
    <h3 className="text-lg font-bold text-teal-400 mb-2">{title}</h3>
    <p className="text-gray-400 text-sm">{description}</p>
  </motion.div>
);

const HomePage = () => {
  return (
    <div className="text-center">
      {/* Hero Section */}
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.7, ease: "easeOut" }}
        className="pt-24 pb-16"
      >
        <h2 className="text-5xl md:text-6xl font-extrabold tracking-tight text-white">
          Chat with My Code.
        </h2>
        <h2 className="text-5xl md:text-6xl font-extrabold tracking-tight text-teal-400 mt-2">
          A Living Portfolio.
        </h2>
        <p className="mt-6 max-w-2xl mx-auto text-lg text-gray-400">
          REPLOIT is an AI-powered co-pilot that understands my projects inside
          and out. Ask questions, explore implementations, and see the code come
          to life.
        </p>
      </motion.div>

      {/* Feature Showcase */}
      <div className="grid md:grid-cols-3 gap-8 mb-16">
        <FeatureCard
          title="Conversational Memory"
          description="Engage in meaningful, multi-turn conversations. The agent remembers the context of your questions to provide accurate, relevant follow-ups."
          animationDelay={0.3}
        />
        <FeatureCard
          title="Live Visualization"
          description="See the AI's thought process in real-time. A 'Glass Engine' modal visualizes the agent's reasoning from retrieval to evaluation."
          animationDelay={0.5}
        />
        <FeatureCard
          title="Accurate Code Analysis"
          description="Powered by a sophisticated RAG pipeline, the agent provides answers grounded in the actual source code, complete with citations."
          animationDelay={0.7}
        />
      </div>

      {/* Call to Action */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 1.0 }}
      >
        <button className="bg-teal-500 hover:bg-teal-600 text-white font-bold py-3 px-8 rounded-lg text-lg transition-all duration-300 transform hover:scale-105">
          Explore My Projects
        </button>
      </motion.div>
    </div>
  );
};

export default HomePage;
