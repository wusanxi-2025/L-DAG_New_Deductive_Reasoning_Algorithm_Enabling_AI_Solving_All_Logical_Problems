import os
import csv
import itertools
import sys
import re

def xor(a, b):
    """XOR operation"""
    return a != b

def parse_logical_expression(expr, variables):
    """Parse a logical expression and return a function to evaluate it"""
    # Clean the expression
    expr = expr.strip()
    
    # Handle negation ¬
    expr = re.sub(r'¬([A-Z])', r'(not \1)', expr)
    
    # Handle XOR (⊕)
    expr = re.sub(r'([A-Z])\s*⊕\s*([A-Z])', r'xor(\1, \2)', expr)
    
    # Handle biconditional (↔) - must be done before implication
    if '↔' in expr:
        parts = expr.split('↔')
        if len(parts) == 2:
            left = parts[0].strip()
            right = parts[1].strip()
            expr = f'({left}) == ({right})'
    
    # Handle implication (→)
    elif '→' in expr:
        parts = expr.split('→')
        if len(parts) == 2:
            left = parts[0].strip()
            right = parts[1].strip()
            expr = f'(not ({left})) or ({right})'
    
    # Handle logical operators
    expr = expr.replace('∧', ' and ')
    expr = expr.replace('∨', ' or ')
    
    print(f"Parsed expression: {expr}")  # Debug output
    
    # Create a function to evaluate the expression
    def evaluate(**kwargs):
        # Create local variables for evaluation
        local_vars = kwargs.copy()
        local_vars['xor'] = xor
        try:
            result = eval(expr, {"__builtins__": {}}, local_vars)
            return result
        except Exception as e:
            print(f"Error evaluating expression: {expr}")
            print(f"Error details: {e}")
            return False
    
    return evaluate

def read_input_file(filename):
    """Read and parse the input file"""
    premises = []
    conclusion = None
    variables = set()
    
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Process each line
    for line in lines:
        line = line.strip()
        # Remove quotes if present
        if line.startswith('"') and line.endswith('"'):
            line = line[1:-1]
        
        # Skip empty lines and certain keywords
        if not line or line.startswith('Variables:') or line == 'Premises:':
            continue
            
        # Find premises (numbered lines)
        premise_match = re.match(r'(\d+)\)\s*(.+)', line)
        if premise_match:
            premise = premise_match.group(2).strip()
            premises.append(premise)
            # Extract variables from premise
            vars_in_premise = re.findall(r'\b[A-Z]\b', premise)
            variables.update(vars_in_premise)
            continue
        
        # Find conclusion
        conclusion_match = re.match(r'Conclusion:\s*(.+)', line)
        if conclusion_match:
            conclusion = conclusion_match.group(1).strip()
            # Extract variables from conclusion
            vars_in_conclusion = re.findall(r'\b[A-Z]\b', conclusion)
            variables.update(vars_in_conclusion)
    
    return premises, conclusion, sorted(list(variables))

def parse_conclusion(conclusion_str):
    """Parse the conclusion expression"""
    # Handle special functions like xor
    conclusion_str = re.sub(r'xor\((\w+),\s*(\w+)\)', r'xor(\1, \2)', conclusion_str)
    
    # Handle logical operators
    conclusion_str = conclusion_str.replace(' and ', ' and ')
    conclusion_str = conclusion_str.replace(' or ', ' or ')
    conclusion_str = conclusion_str.replace(' not ', ' not ')
    
    def evaluate(**kwargs):
        local_vars = kwargs.copy()
        local_vars['xor'] = xor
        try:
            return eval(conclusion_str, {"__builtins__": {}}, local_vars)
        except:
            print(f"Error evaluating conclusion: {conclusion_str}")
            return False
    
    return evaluate

def generate_truth_table(input_filename):
    """Generate the truth table from input file"""
    # Check if input file exists
    if not os.path.exists(input_filename):
        print(f"Error: Input file '{input_filename}' not found.")
        return
    
    # Read and parse input file
    try:
        premises, conclusion, variables = read_input_file(input_filename)
    except Exception as e:
        print(f"Error reading input file: {e}")
        return
    
    if not premises:
        print("No premises found in input file.")
        return
    
    if not conclusion:
        print("No conclusion found in input file.")
        return
    
    print(f"Found {len(premises)} premises and 1 conclusion")
    print(f"Variables: {variables}")
    
    # Generate output filename
    base_name = os.path.splitext(input_filename)[0]
    output_filename = f"{base_name}.out.csv"
    
    # Create premise evaluators
    premise_evaluators = []
    for i, premise in enumerate(premises):
        try:
            evaluator = parse_logical_expression(premise, variables)
            premise_evaluators.append(evaluator)
            print(f"Premise {i+1}: {premise}")
        except Exception as e:
            print(f"Error parsing premise {i+1}: {premise}")
            print(f"Error: {e}")
            return
    
    # Create conclusion evaluator
    try:
        conclusion_evaluator = parse_conclusion(conclusion)
        print(f"Conclusion: {conclusion}")
    except Exception as e:
        print(f"Error parsing conclusion: {conclusion}")
        print(f"Error: {e}")
        return
    
    # Create headers
    premise_cols = [f'C{i+1}' for i in range(len(premises))]
    header = variables + premise_cols + ['All_Premises', 'Conclusion']
    
    # Generate all possible combinations
    num_vars = len(variables)
    rows = []
    
    for combination in itertools.product([0, 1], repeat=num_vars):
        # Create variable assignment
        var_dict = dict(zip(variables, combination))
        
        # Evaluate all premises
        premise_values = []
        for evaluator in premise_evaluators:
            try:
                result = evaluator(**var_dict)
                premise_values.append(int(result))
            except Exception as e:
                print(f"Error evaluating premise with {var_dict}: {e}")
                premise_values.append(0)
        
        # Check if all premises are true
        all_premises = all(premise_values)
        
        # Evaluate conclusion only if all premises are true
        if all_premises:
            try:
                conclusion_result = conclusion_evaluator(**var_dict)
                conclusion_str = str(int(conclusion_result))
            except Exception as e:
                print(f"Error evaluating conclusion with {var_dict}: {e}")
                conclusion_str = "-"
        else:
            conclusion_str = "-"
        
        # Create row
        row = list(combination) + premise_values + [int(all_premises), conclusion_str]
        rows.append(row)
    
    # Write to CSV file
    with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        writer.writerows(rows)
    
    print(f"\nTruth table generated and saved to: {output_filename}")
    
    # Print summary
    valid_rows = [row for row in rows if row[-2] == 1]  # All_Premises = 1
    if valid_rows:
        print(f"\nRows where all premises are true: {len(valid_rows)}")
        print("Conclusion values for these rows:")
        for i, row in enumerate(valid_rows):
            var_values = dict(zip(variables, row[:num_vars]))
            print(f"  Row {i+1}: {var_values} -> Conclusion: {row[-1]}")
    else:
        print("\nNo rows where all premises are true.")

def main():
    """Main function to handle command line arguments"""
    if len(sys.argv) != 2:
        print("Usage: python script.py <input_filename>")
        print("Example: python script.py problem.txt")
        print("\nInput file format:")
        print("1) premise1")
        print("2) premise2")
        print("...")
        print("Conclusion: conclusion_expression")
        sys.exit(1)
    
    input_filename = sys.argv[1]
    generate_truth_table(input_filename)

if __name__ == "__main__":
    main()