import numpy as np
from tespy.networks import Network
from tespy.components import (
    Compressor, Condenser, HeatExchangerSimple, Valve, 
    HeatExchanger, Merge, Splitter, Sink, Source
)
from tespy.connections import Connection
from CoolProp.CoolProp import PropsSI
import pandas as pd


class HeatPump:
    """Single heat pump unit with configurable refrigerant"""
    
    def __init__(self, name, refrigerant, network):
        self.name = name
        self.refrigerant = refrigerant
        self.network = network
        self.components = {}
        self.connections = []
        
        # Create components
        self.components['compressor'] = Compressor(f'{name}_comp')
        self.components['condenser'] = Condenser(f'{name}_cond')
        self.components['valve'] = Valve(f'{name}_valve')
        self.components['evaporator'] = HeatExchangerSimple(f'{name}_evap')
        
        # Add to network
        for comp in self.components.values():
            network.add_comps(comp)
    
    def connect_cycle(self):
        """Connect components in basic cycle"""
        # Refrigerant cycle connections
        c1 = Connection(self.components['evaporator'], 'out1',
                       self.components['compressor'], 'in1',
                       label=f'{self.name}_c1')
        c2 = Connection(self.components['compressor'], 'out1',
                       self.components['condenser'], 'in1',
                       label=f'{self.name}_c2')
        c3 = Connection(self.components['condenser'], 'out1',
                       self.components['valve'], 'in1',
                       label=f'{self.name}_c3')
        c4 = Connection(self.components['valve'], 'out1',
                       self.components['evaporator'], 'in1',
                       label=f'{self.name}_c4')
        
        self.connections = [c1, c2, c3, c4]
        self.network.add_conns(*self.connections)
        
        # Set refrigerant
        for conn in self.connections:
            conn.set_attr(fluid={self.refrigerant: 1})
        
        return c1, c2, c3, c4


class CascadeHeatPumpSystem:
    """Cascade heat pump system with flexible configuration"""
    
    def __init__(self):
        self.network = Network(fluids=['water', 'propane', 'isobutane'])
        self.network.set_attr(p_unit='bar', T_unit='C', h_unit='kJ/kg')
        self.heat_pumps = {}
        self.cascade_hx = None
        self.subcoolers = {}
        
    def add_heat_pump(self, name, refrigerant):
        """Add a heat pump to the system"""
        hp = HeatPump(name, refrigerant, self.network)
        self.heat_pumps[name] = hp
        return hp
    
    def create_cascade(self, hp1_name, hp2_name, cascade_type='condenser-evaporator'):
        """Create cascade connection between two heat pumps"""
        hp1 = self.heat_pumps[hp1_name]
        hp2 = self.heat_pumps[hp2_name]
        
        if cascade_type == 'condenser-evaporator':
            # Replace separate condenser/evaporator with cascade HX
            self.cascade_hx = HeatExchanger(f'cascade_hx_{hp1_name}_{hp2_name}')
            self.network.add_comps(self.cascade_hx)
            
            # Remove old connections and components
            self.network.del_comps(hp1.components['condenser'])
            self.network.del_comps(hp2.components['evaporator'])
            
            # Connect cascade heat exchanger
            # HP1 hot side (condenser)
            c_cas1 = Connection(hp1.components['compressor'], 'out1',
                               self.cascade_hx, 'in1',
                               label=f'cas_{hp1_name}_hot_in')
            c_cas2 = Connection(self.cascade_hx, 'out1',
                               hp1.components['valve'], 'in1',
                               label=f'cas_{hp1_name}_hot_out')
            
            # HP2 cold side (evaporator)
            c_cas3 = Connection(hp2.components['valve'], 'out1',
                               self.cascade_hx, 'in2',
                               label=f'cas_{hp2_name}_cold_in')
            c_cas4 = Connection(self.cascade_hx, 'out2',
                               hp2.components['compressor'], 'in1',
                               label=f'cas_{hp2_name}_cold_out')
            
            self.network.add_conns(c_cas1, c_cas2, c_cas3, c_cas4)
            
            # Set fluids
            c_cas1.set_attr(fluid={hp1.refrigerant: 1})
            c_cas2.set_attr(fluid={hp1.refrigerant: 1})
            c_cas3.set_attr(fluid={hp2.refrigerant: 1})
            c_cas4.set_attr(fluid={hp2.refrigerant: 1})
            
            return self.cascade_hx
    
    def add_subcooler(self, hp_name, subcooler_fluid='isobutane'):
        """Add subcooler to a heat pump"""
        hp = self.heat_pumps[hp_name]
        
        # Create subcooler heat exchanger
        subcooler = HeatExchanger(f'{hp_name}_subcooler')
        self.network.add_comps(subcooler)
        self.subcoolers[hp_name] = subcooler
        
        # Create subcooler cycle components
        sc_comp = Compressor(f'{hp_name}_sc_comp')
        sc_valve = Valve(f'{hp_name}_sc_valve')
        sc_evap = HeatExchangerSimple(f'{hp_name}_sc_evap')
        
        self.network.add_comps(sc_comp, sc_valve, sc_evap)
        
        # Subcooler connections
        # Main cycle side
        # Intercept between condenser and valve
        old_conn = None
        for conn in self.network.conns.values():
            if (conn.source.label == hp.components['condenser'].label and 
                conn.target.label == hp.components['valve'].label):
                old_conn = conn
                break
        
        if old_conn:
            self.network.del_conns(old_conn)
        
        c_sc1 = Connection(hp.components['condenser'], 'out1',
                          subcooler, 'in1',
                          label=f'{hp_name}_to_subcooler')
        c_sc2 = Connection(subcooler, 'out1',
                          hp.components['valve'], 'in1',
                          label=f'{hp_name}_from_subcooler')
        
        # Subcooler cycle
        c_sc3 = Connection(sc_evap, 'out1', sc_comp, 'in1',
                          label=f'{hp_name}_sc_c1')
        c_sc4 = Connection(sc_comp, 'out1', subcooler, 'in2',
                          label=f'{hp_name}_sc_c2')
        c_sc5 = Connection(subcooler, 'out2', sc_valve, 'in1',
                          label=f'{hp_name}_sc_c3')
        c_sc6 = Connection(sc_valve, 'out1', sc_evap, 'in1',
                          label=f'{hp_name}_sc_c4')
        
        self.network.add_conns(c_sc1, c_sc2, c_sc3, c_sc4, c_sc5, c_sc6)
        
        # Set fluids
        c_sc1.set_attr(fluid={hp.refrigerant: 1})
        c_sc2.set_attr(fluid={hp.refrigerant: 1})
        c_sc3.set_attr(fluid={subcooler_fluid: 1})
        c_sc4.set_attr(fluid={subcooler_fluid: 1})
        c_sc5.set_attr(fluid={subcooler_fluid: 1})
        c_sc6.set_attr(fluid={subcooler_fluid: 1})
        
        return subcooler
    
    def create_parallel_cascades(self, cascade_configs):
        """Create multiple cascades in parallel
        cascade_configs: list of tuples [(hp1_name, hp2_name), ...]
        """
        merge_hot = Merge('merge_hot')
        split_cold = Splitter('split_cold')
        self.network.add_comps(merge_hot, split_cold)
        
        # Create individual cascades
        for i, (hp1_name, hp2_name) in enumerate(cascade_configs):
            self.create_cascade(hp1_name, hp2_name)
        
        # Connect to common heat source/sink
        # This would need additional configuration based on specific system
        
    def set_operating_conditions(self, hp_name, evap_temp, cond_temp, 
                                superheat=5, subcooling=5):
        """Set operating conditions for a heat pump"""
        hp = self.heat_pumps[hp_name]
        
        # Find relevant connections
        for conn in self.network.conns.values():
            if conn.source == hp.components['compressor']:
                # Compressor outlet (condenser inlet)
                conn.set_attr(T=cond_temp + 15)  # Discharge temperature
            elif conn.target == hp.components['compressor']:
                # Compressor inlet
                conn.set_attr(T=evap_temp + superheat)
            elif conn.source == hp.components['valve']:
                # Valve outlet (evaporator inlet)
                conn.set_attr(T=evap_temp, x=0.2)  # Two-phase
            elif conn.target == hp.components['valve']:
                # Valve inlet
                conn.set_attr(T=cond_temp - subcooling)
    
    def solve_system(self):
        """Solve the thermodynamic system"""
        self.network.solve('design')
        self.network.print_results()
        
    def calculate_performance(self):
        """Calculate system performance metrics"""
        results = {}
        
        for name, hp in self.heat_pumps.items():
            comp = hp.components['compressor']
            cond = hp.components['condenser']
            evap = hp.components['evaporator']
            
            # Get power consumption and heat duties
            W_comp = comp.P.val  # kW
            Q_cond = cond.Q.val  # kW
            Q_evap = evap.Q.val  # kW
            
            # Calculate COP
            COP = abs(Q_cond / W_comp) if W_comp != 0 else 0
            
            results[name] = {
                'compressor_power': W_comp,
                'condenser_duty': Q_cond,
                'evaporator_duty': Q_evap,
                'COP': COP
            }
        
        # System COP
        total_W = sum(r['compressor_power'] for r in results.values())
        total_Q = sum(r['condenser_duty'] for r in results.values())
        
        results['system'] = {
            'total_power': total_W,
            'total_heating': total_Q,
            'system_COP': abs(total_Q / total_W) if total_W != 0 else 0
        }
        
        return results
    
    def generate_report(self):
        """Generate performance report"""
        perf = self.calculate_performance()
        
        report = "Heat Pump Cascade System Performance Report\n"
        report += "=" * 50 + "\n\n"
        
        for name, data in perf.items():
            if name != 'system':
                report += f"Heat Pump: {name}\n"
                report += f"  Compressor Power: {data['compressor_power']:.2f} kW\n"
                report += f"  Condenser Duty: {data['condenser_duty']:.2f} kW\n"
                report += f"  Evaporator Duty: {data['evaporator_duty']:.2f} kW\n"
                report += f"  COP: {data['COP']:.2f}\n\n"
        
        report += "System Performance:\n"
        report += f"  Total Power: {perf['system']['total_power']:.2f} kW\n"
        report += f"  Total Heating: {perf['system']['total_heating']:.2f} kW\n"
        report += f"  System COP: {perf['system']['system_COP']:.2f}\n"
        
        return report


# Example usage
def example_pr_ib_cascade():
    """Example: Propane/Isobutane cascade system"""
    system = CascadeHeatPumpSystem()
    
    # Add heat pumps
    hp1 = system.add_heat_pump('HP1', 'propane')
    hp2 = system.add_heat_pump('HP2', 'isobutane')
    
    # Connect basic cycles
    hp1.connect_cycle()
    hp2.connect_cycle()
    
    # Create cascade connection
    system.create_cascade('HP1', 'HP2')
    
    # Add heat source and sink
    source_in = Source('heat_source_in')
    source_out = Sink('heat_source_out')
    sink_in = Source('heat_sink_in')
    sink_out = Sink('heat_sink_out')
    
    system.network.add_comps(source_in, source_out, sink_in, sink_out)
    
    # Connect heat source to HP1 evaporator
    c_src1 = Connection(source_in, 'out1', hp1.components['evaporator'], 'in2')
    c_src2 = Connection(hp1.components['evaporator'], 'out2', source_out, 'in1')
    
    # Connect heat sink to HP2 condenser
    c_snk1 = Connection(sink_in, 'out1', hp2.components['condenser'], 'in2')
    c_snk2 = Connection(hp2.components['condenser'], 'out2', sink_out, 'in1')
    
    system.network.add_conns(c_src1, c_src2, c_snk1, c_snk2)
    
    # Set water properties
    c_src1.set_attr(fluid={'water': 1}, T=10, p=2, m=1)
    c_snk1.set_attr(fluid={'water': 1}, T=40, p=2, m=0.5)
    
    # Set operating conditions
    system.set_operating_conditions('HP1', evap_temp=5, cond_temp=30)
    system.set_operating_conditions('HP2', evap_temp=25, cond_temp=60)
    
    # Solve and report
    system.solve_system()
    print(system.generate_report())
    
    return system


def example_parallel_cascades_with_subcooler():
    """Example: Parallel cascades with subcooler"""
    system = CascadeHeatPumpSystem()
    
    # Create multiple cascade units
    for i in range(2):
        hp1 = system.add_heat_pump(f'HP1_{i}', 'propane')
        hp2 = system.add_heat_pump(f'HP2_{i}', 'isobutane')
        hp1.connect_cycle()
        hp2.connect_cycle()
        system.create_cascade(f'HP1_{i}', f'HP2_{i}')
    
    # Add subcooler to one cascade
    system.add_subcooler('HP2_0', 'isobutane')
    
    # Configure and solve
    for i in range(2):
        system.set_operating_conditions(f'HP1_{i}', evap_temp=5, cond_temp=30)
        system.set_operating_conditions(f'HP2_{i}', evap_temp=25, cond_temp=60)
    
    return system


if __name__ == "__main__":
    # Run example
    cascade_system = example_pr_ib_cascade()
