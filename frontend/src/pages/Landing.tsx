import Navbar from '../components/imagica/Navbar';
import Hero from '../components/imagica/Hero';
import PromptEngine from '../components/imagica/PromptEngine';
import HowItWorks from '../components/imagica/HowItWorks';
import FeatureSwitcher from '../components/imagica/FeatureSwitcher';
import RealWorldActions from '../components/imagica/RealWorldActions';
import MissionSection from '../components/imagica/MissionSection';
import DeploymentScene from '../components/imagica/DeploymentScene';
import Footer from '../components/imagica/Footer';
import HeroCanvas from '../components/imagica/HeroCanvas';
import SmoothScroll from '../components/imagica/SmoothScroll';

export default function Landing() {
  return (
    <SmoothScroll>
      <div className="relative min-h-screen">
        {/* Fixed 3D background canvas */}
        <HeroCanvas />

        {/* Fixed navbar overlay */}
        <Navbar />

        {/* Content sections */}
        <main className="relative z-10 w-full overflow-hidden">
          <Hero />
          <PromptEngine />
          <HowItWorks />
          <FeatureSwitcher />
          <RealWorldActions />
          <MissionSection />
          <DeploymentScene />
          <Footer />
        </main>
      </div>
    </SmoothScroll>
  );
}
