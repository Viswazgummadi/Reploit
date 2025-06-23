import { motion } from "framer-motion";

const Header = () => {
  const navItems = ["Home", "Projects", "How It Works", "Deployment"];

  return (
    <motion.header
      className="fixed top-0 left-0 right-0 z-10 bg-gray-950/50 backdrop-blur-md"
      initial={{ y: -100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5, ease: "easeOut" }}
    >
      <div className="container mx-auto max-w-7xl px-4">
        <div className="flex items-center justify-between h-16 border-b border-white/10">
          <h1 className="text-xl font-bold text-teal-400">REPLOIT</h1>
          <nav className="hidden md:flex items-center space-x-8">
            {navItems.map((item) => (
              <a
                key={item}
                href="#"
                className="text-sm text-gray-400 hover:text-white transition-colors"
              >
                {item}
              </a>
            ))}
          </nav>
          <a
            href="#" // This will later link to your GitHub repo
            className="hidden md:block bg-gray-800 hover:bg-gray-700 text-sm text-white font-semibold py-2 px-4 rounded-lg transition-colors"
          >
            Use This Yourself
          </a>
        </div>
      </div>
    </motion.header>
  );
};

export default Header;
